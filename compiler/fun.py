import rule
import cons
from precondition import Precondition
from postcondition import Postcondition


class Fun():
    index = 0

    def __init__(self, name, sig, pre, post, body):
        self.ref = name
        self.id = Fun.index
        self.sig = sig
        self.pre = Precondition(pre, self)
        self.post = Postcondition(post, self)
        self.body = [rule.Rule(r, self) for r in body]
        self.argsSize = len(sig[1])
        Fun.index = Fun.index + 1
        cons.funs[name] = self.id

    def params(self, res=False):
        '''returns Term* x_0, Term* x_1, ..., Term* x_<n-1>'''
        params = ["Term* x_%d" % i for i in range(self.argsSize)]
        if res: params.append('Term* res')
        return ', '.join(params)

    def args(self, res=False):
        '''returns x_0, x_1, ..., x_<n-1>'''
        args = ["x_%d" % i for i in range(self.argsSize)]
        if res: args.append('res')
        return ', '.join(args)

    def prototype(self):
        return '''
Term* f_{id}({0});
void pre_{id}({0});
void post_{id}({1});
'''.format(self.params(), self.params(True), id = self.id)

    def compileFun(self):
        return '''
Term* f_{id}({0}) {{
    pre_{id}({args});
    {body}
    Term* res = new Term;
    res->tag = 1;
    res->refcnt = 0;
    post_{id}({1});
    return res;
}}
'''.format(self.params(), self.args(True), id=self.id, args=self.args(), body=''.join([r.compile() for r in self.body]))

    def compile(self):
        return self.compileFun() + self.pre.compile() + self.post.compile()

