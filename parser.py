from sly import Lexer, Parser
import json

class CalcLexer(Lexer):
    tokens = { FUN, LOWERID, UPPERID, ARROW, COMMA, SIGNATURE, PRECONDITION, POSTCONDITION }
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
    
    @_('FUN LOWERID signatura precondicion postcondicion regla')
    def declaracion(self, p):
        return ('fun', p.LOWERID, p.signatura, p.precondicion, p.postcondicion, p.regla)

    @_('UPPERID ARROW UPPERID')
    def regla(self, p):
        return ('rule', p.UPPERID0, p.UPPERID1)

    @_('SIGNATURE LOWERID')
    def signatura(self, p):
        return ('sig', p.LOWERID)

    @_('empty')
    def signatura(self, p):
        return ('-' )        

    @_('PRECONDITION LOWERID')
    def precondicion(self, p):
        return ('pre', p.LOWERID)

    @_('empty')
    def precondicion(self, p):
        return ('true')        

    @_('POSTCONDITION LOWERID')
    def postcondicion(self, p):
        return ('post', p.LOWERID)

    @_('empty')
    def postcondicion(self, p):
        return ('true')

    @_('')
    def empty(self, p):
        return []

if __name__ == '__main__':
    data = '''
-- esto es un comentario
fun length
    Nil -> Zero
fun length2
: sig2
? balasdasd
! asdasdasdasdasdas    
    Nil2 -> Zero2
'''
    lexer = CalcLexer()
    parser = CalcParser()
    # for tok in lexer.tokenize(data):
    #     print('type=%r, value=%r' % (tok.type, tok.value))
    print(json.dumps(parser.parse(lexer.tokenize(data))))
    # print(parser.parse(lexer.tokenize(data)))
