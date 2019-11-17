import sys
import json
from string import Template
import fun

class Compiler():
    output = ''
    ast = []
    funs = []
    cons = ['True', 'False']
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
/*
//Estas funciones hay que hacerlas
void incref(Term* t){
    t.refcnt = t->refcnt++;
}

void decref(Term* t) {
    t.refcnt = t.refcnt;
    if(t.refcnt == 0) {
        cant_child = t.children.size()
        for(int i = 0; i < cant_child; i++)
        {
            t.children[i].decref();
        }
        delete t;
    }
}
*/

void incref(Term* t);
void decref(Term* t);
void printTerm(Term* t);
void printTerm(Term* t);

$prototypes
$functions
$checks
$prints

int main() {
    $main
    return 0;
}
''')

    @staticmethod
    def getTag(constructor):
        return Compiler.cons.index(constructor)

    @staticmethod
    def compile(data):
        Compiler.ast = json.loads(data)
        Compiler.loadFunctions()
        d = dict(prototypes=Compiler.prototypes(), functions=Compiler.functions(), checks=Compiler.checks(), prints=Compiler.prints(), main=Compiler.main())
        Compiler.output = Compiler.template.substitute(d)

    @staticmethod
    def loadFunctions():
        for f in Compiler.ast[1]:
            Compiler.funs.append(fun.Fun(f[1], f[2], f[3], f[4], f[5]))

    @staticmethod
    def addTerm(rule):
        if rule[0] in ['pcons', 'cons']:
            if not (rule[1] in Compiler.cons):
                Compiler.cons.append(rule[1])
            [Compiler.addTerm(p) for p in rule[2]]

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
        return '//TODO: main'


if __name__ == '__main__':
    filename = sys.argv[1]
    f = open(filename, 'r')
    Compiler.compile(f.read())
    print(Compiler.output)
    archivo = open("cplusplus.cpp", "w")
    archivo.write(Compiler.output)