import sys
import json

class Fun():
    index = 0
    def __init__(self, name, sig, pre, post, body):
        self.ref = name
        self.name = 'f_%d' % Fun.index
        Fun.index = Fun.index + 1
        self.sig = sig
        self.pre = pre
        self.post = post
        self.body = [Rule(rule) for rule in body]

    def params(self):
        return ', '.join(["Term* x_%d" % i for i, x in enumerate(self.sig[1])])

    def compile(self):
        return '''
Term* %s(%s) {
    %s
}
''' % (self.name, self.params(), self.body)

class Rule():
    def __init__(self, rule):
        self.pattern = rule[1]
        self.definition = rule[2]
        [Compiler.addTerm(p) for p in self.pattern]
        Compiler.addTerm(self.definition)

    def __repr__(self):
        return "{%s -> %s}" % (self.pattern.__str__(), self.definition.__str__())

class Compiler():
    output = ''
    ast = ''
    funs = []
    cons = []

    def encabezado(self) :
        output = '''
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
        return output

    def parseJSON(self):
        try:
            filename = sys.argv[1]
            f = open(filename, 'r')
            data = f.read()
        except:
            pass
        self.ast = json.loads(data)

    def searchFunctions(self):
        for f in self.ast[1]:
            self.funs.append(Fun(f[1], f[2], f[3], f[4], f[5]))

    @classmethod
    def addTerm(cls, rule):
        # cls.addTerm(rule[2])
        if rule[0] in ['pcons', 'cons']:
            name = rule[1]
            s = set(cls.cons)
            s.add(rule[1])
            cls.cons = list(s)
            [cls.addTerm(p) for p in rule[2]]

    def searchTerms(self):
        res = list(filter(lambda p: len(p) and p[0] == 'program', self.ast))

if __name__ == '__main__':
    compiler = Compiler()
    archivo = open("prueba.txt", "w")
    archivo.write(compiler.encabezado())
    compiler.parseJSON()
    compiler.searchFunctions()
    for f in compiler.funs: print (f.compile())
