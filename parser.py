from sly import Lexer, Parser
import sys
import json
import datetime

class Funcion() :
    nombrefuncion = ''
    signatura = []
    parametros = []

    def __init__(self, nombre, signatura, parametros) :
        self.nombrefuncion = nombre
        self.signatura = signatura
        self.parametros = parametros
            
    def nombreParametros(self) :
        nombreParametros = []       
        if any(self.parametros) :
            for par in self.parametros :
                if par[0] == 'pcons' :
                    nombreParametros.append(par[1])
                else : 
                    nombreParametros.append('_')
        return nombreParametros

    def cantParam(self, nombre):
        cant = 0
        for param in self.parametros :
            if (param[0] == 'pcons') and (param[1] == nombre) :
                cant = cant + 1 
        return cant

    def validarSignatura(self) :
        return True

    def validarFuncion(self):
        return self.validarParametros() ##and self.validarSignatura()
            
    def validarParametros(self) :      
        if any(self.parametros) :  
            variables = self.variablesEnParametros(self.parametros[0])
            for v in variables :
                if variables.count(v) > 1 :
                    raise NameError('Variable repetida')       
        ## Valida posibles problemas de aridad entre los patrones
        return all(map(lambda p : not self.cantParam(p) > 1 , self.nombreParametros()))
    
    
    def variablesEnParametros(self, parametro):
        variables = []
        print(parametro)
        for p in parametro :
            if p[0] == 'pvar' : 
                # for var in p[1] :
                    variables.append(p[1]) 
            elif p[0] == 'pcons' and not any(p[2]) :
                variables.append(p[1]) 
            elif (p[0] == 'pcons' and any(p[2])) :
                if any(variables) :
                    ## Es necesario hacer una COPIA de la lista, python 
                    ## pierde la referencia a la misma
                    tmp_vars = variables[:]
                    variables = tmp_vars + self.variablesEnParametros(p[2])
                else :
                    print('Entra aca')
                    print(variables)
                    variables = self.variablesEnParametros(p[2])
        print(variables)
        return variables
                

class Declaracion () :
    ## Recibe como parametro el listado completo de declaraciones 
    # para ejecutar validaciones sobre la gramatica generada ##
    funciones = []
    def __init__(self, declaraciones):
        for dec in declaraciones :
            patrones = []
            for d in dec[5] :
                patrones.append(d[1])
            funcion = Funcion(dec[1], [dec[2], dec[3], dec[4]], patrones)
            self.funciones.append(funcion)

    def validarGramatica(self) :
        if not self.validarNombreDeFunciones() :
            raise NameError('Error de sintaxis: Nombre de funcion invalido')       
        if not self.validarCantidadParametrosEnReglas() :
            raise NameError('Error de sintaxis: Aridad de funciones invalido')       
        if not self.validarFunciones() :
            raise NameError('Error de sintaxis: Mismo nombre de parametros en una funcion')    
    

    def getReglas(declaracion) :
        return declaracion[0]
    
    def cantFunciones(self, nombre) :
        cant = 0
        for f in self.funciones :
            if f.nombrefuncion == nombre :
                cant = cant + 1 
        return cant

    def validarCantidadParametrosEnReglas(self) : 
        ## La funcion se encarga de validad que todas las funciones tengan la misma aridad
        if any(self.funciones) and any(self.funciones[0].parametros) :
            cant_base = len(self.funciones[0].parametros[0])
            return all(map(lambda fun : self.evalparametros(fun.parametros, cant_base), self.funciones))
        else : 
            return True
    
    def evalparametros(self, patrones, cant_base) :
        for p in patrones : 
            if len(p) != cant_base :
                return False
        return True
    def validarNombreDeFunciones(self) :
        # Todos los nombres de funciones existen una UNICA vez, un nombre de funcion no puede repetirse
        return all(map(lambda funcion : not (self.cantFunciones(funcion.nombrefuncion) > 1), self.funciones))

    def validarFunciones(self) :
        ok_funciones = []
        for fun in self.funciones :
            ok_funciones.append(fun.validarFuncion())
        return all(ok_funciones)
        

class Signatura () :
    def evalSignatura(self, signatura, reglas) :
        if (len(reglas) > 0 and len(signatura[1]) == 0) :
            for i in range(0, self.getCantidadDeParametros(reglas[0])):
                signatura[1].append("_")
        
        return signatura

    def getCantidadDeParametros(self, regla) :
        return len(regla[1])

    def __repr__(self):
        return [self.sig]

class CalcLexer(Lexer):
    tokens = { FUN, LOWERID, UPPERID, COMMA, ARROW, COLON, QUESTION, BANG, UNDERSCORE, LPAREN, RPAREN, CHECK, TRUE, FALSE, IMP, AND, OR, NOT, EQ, PRINT }
    ignore = ' \t'

    # Tokens
    FUN = r'fun'
    ARROW = r'->'
    COMMA = r','
    COLON = r':'
    QUESTION = r'\?'
    BANG = r'!'
    UNDERSCORE = r'_'
    LPAREN = r'\('
    RPAREN = r'\)'
    CHECK = r'check'
    PRINT = r'print'
    TRUE = r'true'
    FALSE = r'false'
    IMP = r'imp'
    AND = r'and'
    OR = r'or'
    NOT = r'not'
    EQ = r'=='
    LOWERID = r'[a-z][_a-zA-Z0-9]*'
    UPPERID = r'[A-Z][_a-zA-Z0-9]*'

    # Ignored pattern
    ignore_newline = r'\n+'
    ignore_comment = r'--.*'

    # Extra action for newlines
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

class CalcParser(Parser):
    # Get the token list from the lexer (required)
    tokens = CalcLexer.tokens
    debugfile = 'parser.out'
    start = 'program'

    precedence = (
       ('left', COMMA),
       ('left', ARROW)
    )

    @_('declaraciones chequeos prints')
    def program(self, p):
        dec = Declaracion(p.declaraciones)
        ## Se valida la gramatica generada, puede anularse todo tipo de validacion
        ## tapando esta linea
        dec.validarGramatica()
        return ['program', p.declaraciones, p.chequeos, p.prints]
    
    @_('')
    def empty(self, p):
        return []

    ###### DECLARACION DE FUNCIONES ######
    @_('declaraciones declaracion')
    def declaraciones(self, p):
        declaracion_completa = p.declaraciones + [p.declaracion]
        return declaracion_completa
    
    @_('empty')
    def declaraciones(self, p):
        return []

    @_('FUN LOWERID signatura precondicion postcondicion reglas')
    def declaracion(self, p):
        sig = Signatura()
        return ['fun', p.LOWERID, sig.evalSignatura(p.signatura, p.reglas), p.precondicion, p.postcondicion, p.reglas]
    
    @_('COLON parametros ARROW parametro')
    def signatura(self, p):
        return ['sig', p.parametros, p.parametro]
    
    @_('empty')
    def signatura(self, p):
        return ['sig', [], '_']

    @_('empty')
    def precondicion(self, p):
        return ['pre', ['true']]

    @_('QUESTION formulaImpOrAndNeg')
    def precondicion(self, p):
        return ['pre', p.formulaImpOrAndNeg]

    @_('empty')
    def postcondicion(self, p):
        return ['post', ['true']]
    
    @_('BANG formulaImpOrAndNeg')
    def postcondicion(self, p):
        return ['post', p.formulaImpOrAndNeg]

    ##### CHEQUEOS #####
    @_('chequeos chequeo')
    def chequeos(self, p):
        return p.chequeos + [p.chequeo]
    
    @_('empty')
    def chequeos(self, p):
        return []
    
    @_('CHECK formulaImpOrAndNeg')
    def chequeo(self, p):
        return ['check', p.formulaImpOrAndNeg]

    ##### PRINT #####
    @_('prints prnt')
    def prints(self, p):
        return p.prints + [p.prnt]

    @_('empty')
    def prints(self, p):
        return []

    @_('PRINT expresion')
    def prnt(self, p):
        return ['print', p.expresion]        

    ###### PARAMETROS DE ASIGNATURAS ######
    @_('empty')
    def parametros(self, p):
        return []
    
    @_('parametro')
    def parametros(self, p):
        return [p.parametro]
    
    @_('parametros COMMA parametros')
    def parametros(self, p):
        return p.parametros0 + p.parametros1
    
    @_('UNDERSCORE', 'LOWERID')
    def parametro(self, p):
        return p[0] 

    ###### REGLAS DE PATTERN MATCHING ######
    @_('empty')
    def reglas(self, p):
        return []
    
    @_('reglas regla')
    def reglas(self, p):
        return p.reglas + [p.regla]
    
    @_('patrones ARROW expresion')
    def regla(self, p):
        return ['rule', p.patrones, p.expresion]
    
    @_('empty')
    def patrones(self, p):
        return []
    
    @_('patron')
    def patrones(self, p):
        return [p.patron]
    
    @_('patrones COMMA patrones')
    def patrones(self, p):
        return p.patrones0 + p.patrones1

    @_('UNDERSCORE')
    def patron(self, p):
        return ['pwild']
    
    @_('LOWERID')
    def patron(self, p):
        return ['pvar', p.LOWERID]
    
    @_('UPPERID')
    def patron(self, p):
        return ['pcons', p.UPPERID, []]
    
    @_('UPPERID LPAREN patrones RPAREN')
    def patron(self, p):
        return ['pcons', p.UPPERID, p.patrones]
    
    @_('LOWERID')
    def expresion(self, p):
        return ['var', p.LOWERID]
    
    @_('UPPERID')
    def expresion(self, p):
        return  ['cons', p.UPPERID, []]
    
    @_('UPPERID LPAREN expresiones RPAREN')
    def expresion(self, p):
        return ['cons', p.UPPERID, p.expresiones]

    @_('LOWERID LPAREN expresiones RPAREN')
    def expresion(self, p):
        return ['app', p.LOWERID, p.expresiones]

    @_('empty')
    def expresiones(self, p):
        return []

    @_('expresion')
    def expresiones(self, p):
        return [p.expresion]
    
    @_('expresiones COMMA expresiones')
    def expresiones(self, p):
        return p.expresiones0 + p.expresiones1
    
    ##### FORMULAS LOGICAS #####
    @_('formulaAtomica')
    def formulaNeg(self, p):
        return p.formulaAtomica

    @_('NOT formulaNeg')
    def formulaNeg(self, p):
        return ['not', p.formulaNeg]

    @_('formulaNeg')
    def formulaAndNeg(self, p):
        return p.formulaNeg

    @_('formulaNeg AND formulaAndNeg')
    def formulaAndNeg(self, p):
        return ['and', p.formulaNeg, p.formulaAndNeg]

    @_('formulaAndNeg OR formulaOrAndNeg')
    def formulaOrAndNeg(self, p):
        return ['or', p.formulaAndNeg, p.formulaOrAndNeg]

    @_('formulaAndNeg')
    def formulaOrAndNeg(self, p):
        return p.formulaAndNeg

    @_('formulaOrAndNeg IMP formulaImpOrAndNeg')
    def formulaImpOrAndNeg(self, p):
        return ['imp', p.formulaOrAndNeg, p.formulaImpOrAndNeg]

    @_('formulaOrAndNeg')
    def formulaImpOrAndNeg(self, p):
        return p.formulaOrAndNeg

    @_('TRUE')
    def formulaAtomica(self, p):
        return ['true']

    @_('FALSE')
    def formulaAtomica(self, p):
        return ['false']
    
    @_('expresion')
    def formulaAtomica(self, p):
        return ['equal', p.expresion, ['cons', 'True', []]]
    
    @_('expresion EQ expresion')
    def formulaAtomica(self, p):
        return ['equal', p.expresion0, p.expresion1]

    @_('LPAREN formulaImpOrAndNeg RPAREN')
    def formulaNeg(self, p):
        return p.formulaImpOrAndNeg

if __name__ == '__main__':
    data = '''
        fun f A(B(x, x), m), B(m) -> B
'''
# Casos de falla 
# Falla por problema de aridad
# fun s A(x), A(y) -> B
#               A(x) -> B

# Falla por problema de variable repetida
# fun f A(B(w, x), m), B(o) -> B

# Falla por problema de nombres de funcion
# fun f A(B(w, x), m), B(m) -> B
# fun f A(B(w, x), m), B(n) -> B
        

    # lexer = CalcLexer()
    # parser = CalcParser()
    
    # for tok in lexer.tokenize(data):
    #      print('type=%r, value=%r' % (tok.type, tok.value))
    # print(parser.parse(lexer.tokenize(data)))
    
    # json = json.dumps(parser.parse(lexer.tokenize(data)))
    
    # print(json)


    # lexer = CalcLexer()
    # parser = CalcParser()
    # json = json.dumps(parser.parse(lexer.tokenize(data)))


    try:
        filename = sys.argv[1]
        f = open(filename, 'r')
        data = f.read()
    except:
        pass
    lexer = CalcLexer()
    parser = CalcParser()
    json = json.dumps(parser.parse(lexer.tokenize(data)))
    print(json)
    f = open('./output.json', 'w')
    f.write(json)
