from sly import Lexer, Parser

class CalcLexer(Lexer):
    tokens = { FUN, LOWERID, UPPERID, ARROW, COMMA, SIGNATURA, UNDERSCORE, PRECONDICION, POSTCONDICION }
    ignore = ' \t'

    # Tokens
    FUN = r'fun'
    LOWERID = r'[a-z][_a-zA-Z0-9]*'
    UPPERID = r'[A-Z][_a-zA-Z0-9]*'
    ARROW = r'->'
    COMMA = r','
    SIGNATURA = r':'
    UNDERSCORE = r'_'
    PRECONDICION = r'\?'
    POSTCONDICION = r'!'

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
    
    @_('FUN LOWERID signature')
    def declaracion(self, p):
        return ('fun', p.LOWERID, p.signature)

    @_('SIGNATURA precondicion regla')
    def signature(self, p):
        return (':', p.precondicion + p.regla)
    
    @_('SIGNATURA precondicion postcondicion regla')
    def signature(self, p):
        return (':', p.precondicion + p.postcondicion + p.regla)
  
    @_('SIGNATURA regla')
    def signature(self, p):
        return (':', p.regla)
    
    @_('PRECONDICION LOWERID')
    def precondicion(self, p):
        return ('?', p.LOWERID)
    
    @_('POSTCONDICION LOWERID')
    def postcondicion(self, p):
        return ('!', p.LOWERID)


    @_('UNDERSCORE ARROW UPPERID regla')
    def regla(self, p):
        return ('rule', p.UNDERSCORE, p.UPPERID)
    
    @_('UNDERSCORE ARROW UPPERID')
    def regla(self, p):
        return ('rule', p.UNDERSCORE, p.UPPERID)


    @_('UPPERID ARROW UPPERID')
    def regla(self, p):
        return ('rule', p.UPPERID0, p.UPPERID1)

    @_('')
    def empty(self, p):
        return []

if __name__ == '__main__':
    data = '''
-- esto es un comentario
fun length : 
? pruebaprecondicion
! pruebapostcondicion
    _ -> Zero
    x -> x
'''
    lexer = CalcLexer()
    parser = CalcParser()
    # for tok in lexer.tokenize(data):
    #     print('type=%r, value=%r' % (tok.type, tok.value))
    print(parser.parse(lexer.tokenize(data)))
