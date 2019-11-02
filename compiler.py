import sys
import json

class Compiler():
    output = ''
    ast = ''

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
        # print(self.ast)

    def searchTerms(self):
        res = list(filter(lambda p: len(p) and p[0] == 'program', self.ast))
        print(res)

if __name__ == '__main__':
    compiler = Compiler()
    archivo = open("prueba.txt", "w")
    archivo.write(compiler.encabezado())
    compiler.parseJSON()
    compiler.searchTerms()