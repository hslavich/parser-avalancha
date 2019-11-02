import sys
import json

class Fun():
    def __init__(self, name, sig, pre, post, body):
        self.name = name
        self.sig = sig
        self.pre = pre
        self.post = post
        self.body = body

class Compiler():
    output = ''
    ast = ''
    funs = []

    def encabezado(self) :
        output = '''
#include <vector>
#include <string>
#include <iostream>
using namespace std;
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


    def searchTerms(self):
        res = list(filter(lambda p: len(p) and p[0] == 'program', self.ast))

if __name__ == '__main__':
    compiler = Compiler()
    archivo = open("prueba.txt", "w")
    archivo.write(compiler.encabezado())
    compiler.parseJSON()
    compiler.searchFunctions()
    for f in compiler.funs: print (f.name, f.sig)