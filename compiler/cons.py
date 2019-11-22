cons = ['True', 'False']

def addCons(c):
    global cons
    cons.append(c)

varIndex = 0

def getNewVar():
    global varIndex
    var = 't_%d' % varIndex
    varIndex = varIndex + 1
    return var

funs = {}
