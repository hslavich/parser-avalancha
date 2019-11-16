from compiler import Compiler

class Rule():
    def __init__(self, rule):
        [Compiler.addTerm(p) for p in rule[1]]
        Compiler.addTerm(rule[2])
        self.vars = {}
        self.patterns = [Pattern(p, self, i) for i, p in enumerate(rule[1])]
        self.expr = Expression(rule[2], self)

    def conditions(self):
        cond = ' && '.join([p.compile() for p in self.patterns])
        return cond if cond else 'true'

    def compile(self):
        return '''
    if ({cond}) {{ {expr}    }}
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
    def __init__(self, expr, rule):
        self.type = expr[0]
        self.expr = expr
        self.rule = rule

    def compile(self):
        return '''
        //TODO
        %s
        //{0!r}
'''.format(self.rule.vars) % (self.evalExpresion())

    def evalExpresion(self):
        if(self.type == 'cons'):
            return '''
        Term* t_n = new Term;
        t_n->tag = {tag};
        t_n->refcnt = 0;
        addChildren(t_n, ...);
    '''.format(tag=Compiler.getTag(self.expr[1]))

        if(self.type == 'var'):
            return '''
        Term* t_n = {0}
    '''.format(self.rule.vars[self.expr[1]])
            
        if(self.type == 'app'):
            return '''
        incref({arg});
        Term* t_2 = {fun}({arg});
        decref({arg});
    '''.format(fun='f_22', arg='x_33')            