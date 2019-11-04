import sys
import json

class Fun():
    index = 0

    def __init__(self, name, sig, pre, post, body):
        self.ref = name
        self.id = Fun.index
        self.sig = sig
        self.pre = pre
        self.post = post
        self.body = [Rule(rule) for rule in body]
        self.argsSize = len(sig[1])
        Fun.index = Fun.index + 1
        Compiler.addOutput(self.prototype())

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

    def compileF(self):
        return '''
Term* f_{id}({0}) {{
    pre_{id}({args});

    //Aca falta todo lo de pattern matching

    post_{id}({args}, res);
    return res;
}}
'''.format(self.params(), id=self.id, args=self.args())

    def compilePre(self):
        return '''
void pre_{id}({0}) {{
    // Aca todo el codigo de la funcion precondicion
}}
'''.format(self.params(), id=self.id)

    def compilePost(self):
        return '''
void post_{id}({0}, Term* res) {{
    // Aca todo el codigo de la funcion postcondicion
}}
'''.format(self.params(), id = self.id)

    def compile(self):
        Compiler.addOutput(self.compileF())
        Compiler.addOutput(self.compilePre())
        Compiler.addOutput(self.compilePost())

class Rule():
    def __init__(self, rule):
        self.pattern = rule[1]
        self.definition = rule[2]
        [Compiler.addTerm(p) for p in self.pattern]
        Compiler.addTerm(self.definition)

    def __repr__(self):
        return "{%r -> %r}" % (self.pattern, self.definition)

class Compiler():
    output = ''
    ast = []
    funs = []
    cons = []
    header = '''
#include <vector>
#include <string>
#include <iostream>
using namespace std;

typedef int Tag;
struct Term {
    Tag tag;
    vector<Term*> children;
    int refcnt;
};
'''

    @staticmethod
    def compile(data):
        Compiler.ast = json.loads(data)
        Compiler.addOutput(Compiler.header)
        Compiler.loadFunctions()
        Compiler.loadChecks()
        Compiler.loadPrints()
        [f.compile() for f in Compiler.funs]

    @staticmethod
    def loadFunctions():
        for f in Compiler.ast[1]:
            Compiler.funs.append(Fun(f[1], f[2], f[3], f[4], f[5]))

    @staticmethod
    def loadChecks():
        # Compiler.ast[2]
        pass

    @staticmethod
    def loadPrints():
        # Compiler.ast[3]
        pass

    @staticmethod
    def addTerm(rule):
        if rule[0] in ['pcons', 'cons']:
            if not (rule[1] in Compiler.cons):
                Compiler.cons.append(rule[1])
            [Compiler.addTerm(p) for p in rule[2]]

    @staticmethod
    def addOutput(output):
        Compiler.output = Compiler.output + output


if __name__ == '__main__':
    filename = sys.argv[1]
    f = open(filename, 'r')
    Compiler.compile(f.read())
    print(Compiler.output)
