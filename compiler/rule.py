from compiler import Compiler

class Rule():
    def __init__(self, rule):
        [Compiler.addTerm(p) for p in rule[1]]
        Compiler.addTerm(rule[2])
        self.patterns = [Pattern(p, i) for i, p in enumerate(rule[1])]
        self.expr = Expression(rule[2])

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

    def __init__(self, pattern, index, parent=None):
        self.pattern = pattern
        self.parent = parent
        self.index = index #orden de la variable x_1, ..., x_n
        self.type = pattern[0] #pvar | pcons | pwild
        if self.type == 'pcons':
            self.tag = Compiler.getTag(pattern[1])
            self.children = [Pattern(p, i, self) for i, p in enumerate(pattern[2])]

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
    def __init__(self, expr):
        self.type = expr[0]
        self.expr = expr

    def compile(self):
        return '''
        //TODO
        return %s
        //{0!r}
'''.format(self.expr) % (self.expr[1])