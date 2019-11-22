import sys
import json
import pdb
from string import Template
import fun
import cons
import rule

class Compiler():
    output = ''
    ast = []
    funs = []
    template = Template('''
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

void incref(Term* t) {
    t->refcnt = t->refcnt++;
}

void decref(Term* t) {
    if (t->refcnt == 0) {
        for(int i = 0; i < t->children.size(); i++) {
            decref(t->children[i]);
        }
        delete t;
    }
}

$prototypes
$functions
$checks

void printTerm(Term* t) {
    string c;
    $print
}

int main() {
    $main
    return 0;
}
''')

    @staticmethod
    def getTag(constructor):
        if not (constructor in cons.cons):
            cons.addCons(constructor)
        return cons.cons.index(constructor)

    @staticmethod
    def compile(data):
        Compiler.ast = json.loads(data)
        Compiler.loadFunctions()
        f = Compiler.functions()
        p = Compiler.prototypes()
        d = dict(prototypes=p, functions=f, checks=Compiler.checks(), prints=Compiler.prints(), main=Compiler.main())
        d['print'] = Compiler.compilePrint()
        Compiler.output = Compiler.template.substitute(d)

    @staticmethod
    def loadFunctions():
        for f in Compiler.ast[1]:
            Compiler.funs.append(fun.Fun(f[1], f[2], f[3], f[4], f[5]))

    @staticmethod
    def compilePrint():
        c = ['case %d: c = "%s"; break;' % (i, c) for i, c in enumerate(cons.cons)]
        return '''
    switch (t->tag) {{
        {0}
        default: c = "";
    }}
    cout << c;
    for(int i = 0; i < t->children.size(); i++) {{
        cout << "(";
        printTerm(t->children[i]);
        cout << ")";
    }}
'''.format('\n\t'.join(c))

    @staticmethod
    def prototypes():
        return ''.join([f.prototype() for f in Compiler.funs])

    @staticmethod
    def functions():
        return ''.join([f.compile() for f in Compiler.funs])

    @staticmethod
    def checks():
        return '//TODO: checks'

    @staticmethod
    def prints():
        return '//TODO: prints'

    @staticmethod
    def main():
        main = ''
        for print in Compiler.ast[3]:
            expression = rule.Expression(print[1])
            main += '''
        // %r''' % print[1]
            main += expression.compile()
            main += '''
        printTerm(%s); cout << endl;''' % expression.var
        return main


if __name__ == '__main__':
    filename = sys.argv[1]
    f = open(filename, 'r')
    Compiler.compile(f.read())
    print(Compiler.output)
    archivo = open("cplusplus.cpp", "w")
    archivo.write(Compiler.output)
