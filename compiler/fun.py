from rule import Rule
from precondition import Precondition
from postcondition import Postcondition


class Fun():
    index = 0

    def __init__(self, name, sig, pre, post, body):
        self.ref = name
        self.tIndex = 0
        self.id = Fun.index
        self.sig = sig
        self.pre = Precondition(pre, self)
        self.post = Postcondition(post, self)
        self.body = [Rule(rule, self) for rule in body]
        self.argsSize = len(sig[1])
        Fun.index = Fun.index + 1

    def getNewVar(self):
        var = 't_%d' % self.tIndex
        self.tIndex = self.tIndex + 1
        return var

    def params(self):
        '''returns Term* x_0, Term* x_1, ..., Term* x_<n-1>'''
        return ', '.join(["Term* x_%d" % i for i in range(self.argsSize)])

    def args(self):
        '''returns x_0, x_1, ..., x_<n-1>'''
        return ', '.join(["x_%d" % i for i in range(self.argsSize)])

    def prototype(self):
        return '''
Term* f_{id}({0});
void pre_{id}({0});
void post_{id}({0}, Term* res);
'''.format(self.params(), id = self.id)

    def compileFun(self):
        return '''
Term* f_{id}({0}) {{
    pre_{id}({args});
    {body}
    Term* res = new Term;
    res->tag = 1;
    post_{id}({args}, res);
    return res;
}}
'''.format(self.params(), id=self.id, args=self.args(), body=''.join([r.compile() for r in self.body]))

    def compile(self):
        return self.compileFun() + self.pre.compile() + self.post.compile()

