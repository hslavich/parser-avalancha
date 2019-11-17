from compiler import Compiler

class Rule():
    def __init__(self, rule, fun):
        [Compiler.addTerm(p) for p in rule[1]]
        Compiler.addTerm(rule[2])
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
            self.tag = Compiler.getTag(pattern[1])
            self.children = [Pattern(p, rule, i, self) for i, p in enumerate(pattern[2])]
        if self.type == 'pvar':
            self.rule.vars[pattern[1]] = self.var()

    def compile(self):
        if (self.type == 'pcons'):
            childs = [c.compile() for c in self.children if (c.type == 'pcons')]
            var = ['%s->tag == %s' % (self.var(), self.tag)] + childs
            return ' && '.join(var)
        #REVISAR ESTO ------------------------------------------
        if(self.type == 'pvar'):
            return self.pattern[1] + '_' + str(self.index) + '->tag == 1'
        if(self.type == 'pwild'):
            return 'true'            
        #-------------------------------------------------------    
        return ''

    def var(self):
        if self.parent is None:
            return 'x_%s' % self.index
        return '%s->children[%s]' % (self.parent.var(), self.index)


class Expression():
    def __init__(self, expr, rule, parent=None):
        self.type = expr[0]
        self.expr = expr
        self.rule = rule
        self.var = rule.fun.getNewVar()
        self.parent = parent
        self.children = []
        if self.type in ['cons', 'app']:
            self.children = [Expression(e, rule, self) for e in self.expr[2]]

    def compile(self):
        if(self.type == 'cons'):
            expr = '''
        {children}
        Term* {var} = new Term;
        {var}->tag = {tag};
        {var}->refcnt = 0;
        std::vector<Term*> c_{var} {{ {child} }}; 
        {var}->children = c_{var};
'''.format(var=self.var, child=', '.join([c.var for c in self.children]), tag=Compiler.getTag(self.expr[1]), children=''.join([c.compile() for c in self.children]))

        if(self.type == 'var'):
            expr = '''
        Term* {var} = {0};
'''.format(self.rule.vars[self.expr[1]], var=self.var)
            
        if(self.type == 'app'):
            expr = '''
        {children}
        //incref([{arg}]);
        Term* {var} = f_{fun}({arg});
        //decref([{arg}]);
'''.format(var=self.var, fun=self.rule.fun.id, arg=', '.join([c.var for c in self.children]), children=''.join([c.compile() for c in self.children]))

        if self.parent is None:
            expr = expr + '''
        Term* res = {var};
        post_{id}({args}, res);
        return res;
'''.format(var=self.var, id=self.rule.fun.id, args=self.rule.fun.args())
        return expr