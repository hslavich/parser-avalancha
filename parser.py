from sly import Lexer, Parser
import sys
import json

class CalcLexer(Lexer):
    tokens = { FUN, LOWERID, UPPERID, COMMA, ARROW, COLON, QUESTION, BANG, UNDERSCORE, LPAREN, RPAREN }
    ignore = ' \t'

    # Tokens
    FUN = r'fun'
    LOWERID = r'[a-z][_a-zA-Z0-9]*'
    UPPERID = r'[A-Z][_a-zA-Z0-9]*'
    ARROW = r'->'
    COMMA = r','
    COLON = r':'
    QUESTION = r'\?'
    BANG = r'!'
    UNDERSCORE = r'_'
    LPAREN = r'\('
    RPAREN = r'\)'

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

    start = 'program'

    @_('declaraciones')
    def program(self, p):
        return ['program', p.declaraciones, []]
    
    @_('')
    def empty(self, p):
        return []

    ###### DECLARACION DE FUNCIONES ######
    @_('declaraciones declaracion')
    def declaraciones(self, p):
        return p.declaraciones + [p.declaracion]
    
    @_('empty')
    def declaraciones(self, p):
        return []
    
    @_('FUN LOWERID signatura precondicion postcondicion reglas')
    def declaracion(self, p):
        return ['fun', p.LOWERID, p.signatura, p.precondicion, p.postcondicion, p.reglas]
    
    @_('COLON parametros ARROW parametro')
    def signatura(self, p):
        return ['sig', p.parametros, p.parametro]
    
    @_('empty')
    def signatura(self, p):
        return ['sig', [], '_']

    @_('empty')
    def precondicion(self, p):
        return ['pre', ['true']]

    @_('empty')
    def postcondicion(self, p):
        return ['post', ['true']]

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

if __name__ == '__main__':
    data = '''
-- esto es un comentario
fun cero -> Zero
'''
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
