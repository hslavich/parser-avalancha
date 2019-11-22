import compiler
import cons

class Rule():
    def __init__(self, rule, fun):        
        self.fun = fun
        self.vars = {}
        self.patterns = [Pattern(p, self, i) for i, p in enumerate(rule[1])]
        self.expr = Expression(rule[2], self)

    def conditions(self):
        cond = ' && '.join([p.compile() for p in self.patterns])
        return cond if cond else 'true'

    def compile(self):
        return '''
    if ({cond}) {{ {expr}
    }}
'''.format(cond=self.conditions(), expr=self.expr.compile())


class Pattern():
    def __repr__(self):
        return str(self.pattern)

    def __init__(self, pattern, rule, index, parent=None):
        self.rule = rule
        self.pattern = pattern
        self.parent = parent
        self.index = index #orden de la variable x_1, ..., x_n
        self.type = pattern[0] #pvar | pcons | pwild
        if self.type == 'pcons':
            self.tag = compiler.Compiler.getTag(pattern[1])
            self.children = [Pattern(p, rule, i, self) for i, p in enumerate(pattern[2])]
        if self.type == 'pvar':
            self.rule.vars[pattern[1]] = self.var()

    def compile(self):
        if (self.type == 'pcons'):
            childs = [c.compile() for c in self.children if (c.type == 'pcons')]
            var = ['%s->tag == %s' % (self.var(), self.tag)] + childs
            return ' && '.join(var)
        if (self.type in ['pvar', 'pwild']):
            return 'true'            
        return ''

    def var(self):
        if self.parent is None:
            return 'x_%s' % self.index
        return '%s->children[%s]' % (self.parent.var(), self.index)


class Expression():
    def __init__(self, expr, rule=None, parent=None):
        self.type = expr[0]
        self.expr = expr
        self.rule = rule
        self.var = cons.getNewVar()
        self.parent = parent
        self.children = []
        if self.type in ['cons', 'app']:
            self.children = [Expression(e, rule, self) for e in self.expr[2]]

    def compile(self):
        if (self.type == 'cons'):
            expr = self.compileCons()
        elif (self.type == 'var'):
            expr = self.compileVar()
        elif (self.type == 'app'):
            expr = self.compileApp()

        if (self.parent is None) and not (self.rule is None):
            expr = expr + '''
        Term* res = {var};
        post_{id}({args});
        return res;
'''.format(var=self.var, id=self.rule.fun.id, args=self.rule.fun.args(True))
        return expr

    def compileCons(self):
        return '''
        {children}
        Term* {var} = new Term;
        {var}->tag = {tag};
        {var}->refcnt = 0;
        vector<Term*> c_{var} {{{child}}}; 
        {var}->children = c_{var};
'''.format(var=self.var, child=', '.join([c.var for c in self.children]), tag=compiler.Compiler.getTag(self.expr[1]), children=''.join([c.compile() for c in self.children]))

    def compileVar(self):
        return '''
        Term* {var} = {0};
'''.format(self.rule.vars[self.expr[1]], var=self.var)

    def compileApp(self):
        return '''
        {children}
        {incref}
        Term* {var} = f_{fun}({arg});
        {decref}
'''.format(var=self.var, fun=cons.funs[self.expr[1]], arg=', '.join([c.var for c in self.children]), incref=self.callForTerms('incref'), decref=self.callForTerms('decref'), children=''.join([c.compile() for c in self.children]))

    def callForTerms(self, function):
        return ' '.join(['%s(%s);' % (function, c.var) for c in self.children])
