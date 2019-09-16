from sly import Lexer, Parser
import json

class CalcLexer(Lexer):
    tokens = { FUN, LOWERID, UPPERID, ARROW, COMMA, SIGNATURE, PRECONDITION, POSTCONDITION, LPAREN, RPAREN, UNDERSCORE }
    ignore = ' \t'

    # Tokens
    FUN = r'fun'
    LOWERID = r'[a-z][_a-zA-Z0-9]*'
    UPPERID = r'[A-Z][_a-zA-Z0-9]*'
    ARROW = r'->'
    COMMA = r','
    SIGNATURE = r':'
    PRECONDITION = r'\?'
    POSTCONDITION = r'!'
    LPAREN = r'\('
    RPAREN = r'\)'
    UNDERSCORE = r'_'

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
        return ('program', p.declaraciones)

    @_('declaraciones declaracion')
    def declaraciones(self, p):
        return p.declaraciones + [p.declaracion]
    
    @_('empty')
    def declaraciones(self, p):
        return []
    
    @_('FUN LOWERID signatura')
    def declaracion(self, p):
        return ('fun', p.LOWERID, p.signatura)

    @_('SIGNATURE listaparametros')
    def signatura(self, p):
        return ('sig', p.listaparametros)
    
    @_('empty')
    def listaparametros(self, p):
        return ''

    @_('listaParametrosNoVacia')
    def listaparametros(self, p):
        return (p.listaParametrosNoVacia)    
    
    @_('UNDERSCORE')
    def listaParametrosNoVacia(self, p):
        return ('_')
    
    @_('LOWERID')
    def listaParametrosNoVacia(self, p):
        return (p.LOWERID)

    # @_('listaParametrosNoVacia COMMA parametro')
    # def listaParametrosNoVacia(self, p):
    #     return ''

    @_('')
    def empty(self, p):
        return []

if __name__ == '__main__':
#     data = '''
# -- esto es un comentario
# fun length
# : sadsdasdasdasd
# ? blabla
# ! asdasds
#     Nil -> Zero
# fun length2
# : sig2
# ? balasdasd
# ! asdasdasdasdasdas    
#     Nil2 -> Zero2
# '''
    data = '''
        fun foo4
            : x -> x
            x -> x
    '''
lexer = CalcLexer()
parser = CalcParser()
# for tok in lexer.tokenize(data):
#     print('type=%r, value=%r' % (tok.type, tok.value))
print(json.dumps(parser.parse(lexer.tokenize(data))))
# print(parser.parse(lexer.tokenize(data)))
