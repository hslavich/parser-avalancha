from sly import Lexer, Parser
import json

class CalcLexer(Lexer):
    tokens = { FUN, ARROW, COMMA, SIGNATURE, PRECONDITION, POSTCONDITION, IMP, AND, OR, NOT, TRUE, FALSE, LPAREN, RPAREN, LOWERID, UPPERID }
    ignore = ' \t'

    # Tokens
    FUN = r'fun'
    ARROW = r'->'
    COMMA = r','
    SIGNATURE = r':'
    PRECONDITION = r'\?'
    POSTCONDITION = r'!'
    IMP = r'imp'
    AND = r'and'
    OR = r'or'
    NOT = r'not'
    TRUE = r'true'
    FALSE = r'false'
    LPAREN = r'\('
    RPAREN = r'\)'
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

    start = 'precondicion'

    # @_('declaraciones')
    # def program(self, p):
    #     return ('program', p.declaraciones)

    # @_('declaraciones declaracion')
    # def declaraciones(self, p):
    #     return p.declaraciones + [p.declaracion]
    
    # @_('empty')
    # def declaraciones(self, p):
    #     return []
    
    # @_('FUN LOWERID signatura precondicion postcondicion regla')
    # def declaracion(self, p):
    #     return ('fun', p.LOWERID, p.signatura, p.precondicion, p.postcondicion, p.regla)

    # @_('UPPERID ARROW UPPERID')
    # def regla(self, p):
    #     return ('rule', p.UPPERID0, p.UPPERID1)

    # @_('SIGNATURE LOWERID')
    # def signatura(self, p):
    #     return ('sig', p.LOWERID)

    # @_('empty')
    # def signatura(self, p):
    #     return ('-' )        

    # @_('PRECONDITION LOWERID')
    # def precondicion(self, p):
    #     return ('pre', p.LOWERID)

    # @_('empty')
    # def precondicion(self, p):
    #     return ('true')                

    # @_('POSTCONDITION LOWERID')
    # def postcondicion(self, p):
    #     return ('post', p.LOWERID)

    # @_('empty')
    # def postcondicion(self, p):
    #     return ('true')

    ##################################################################################################################

    # @_('PRECONDITION formulaImpOrAndNeg')
    # def precondicion(self, p):
    #     return ('pre', p.formulaImpOrAndNeg)

    # @_('empty')
    # def precondicion(self, p):
    #     return ('true')

    # @_('formulaImpOrAndNeg IMP formulaOrAndNeg formulaOrAndNeg')
    # def formulaImpOrAndNeg(self, p):
    #     return (p.formulaImpOrAndNeg, ' imp ', p.formulaOrAndNeg, p.formulaOrAndNeg)

    ################# BORRAR #################
    # @_('PRECONDITION formulaAtomica')
    # def precondicion(self, p):
    #     return ('pre', [p.formulaAtomica])
    
    # @_('PRECONDITION formulaNeg')
    # def precondicion(self, p):
    #     return ('pre', [p.formulaNeg])

    @_('PRECONDITION formulaImpOrAndNeg')
    def precondicion(self, p):
        return ('pre', p.formulaImpOrAndNeg)
    ##########################################

    @_('formulaAtomica')
    def formulaNeg(self, p):
        return p.formulaAtomica

    @_('NOT formulaNeg')
    def formulaNeg(self, p):
        return ('not ', p.formulaNeg)

    @_('formulaNeg')
    def formulaAndNeg(self, p):
        return (p.formulaNeg)        

    @_('formulaAndNeg AND formulaNeg')
    def formulaAndNeg(self, p):
        return ('and', p.formulaAndNeg, p.formulaNeg)

    @_('formulaOrAndNeg OR formulaAndNeg')
    def formulaOrAndNeg(self, p):
        return ('or', p.formulaOrAndNeg, p.formulaAndNeg)

    @_('formulaAndNeg')
    def formulaOrAndNeg(self, p):
        return (p.formulaAndNeg)

    @_('formulaImpOrAndNeg IMP formulaOrAndNeg')
    def formulaImpOrAndNeg(self, p):
        return ('imp', p.formulaImpOrAndNeg, p.formulaOrAndNeg)

    @_('formulaOrAndNeg')
    def formulaImpOrAndNeg(self, p):
        return (p.formulaOrAndNeg)

    @_('empty')
    def formulaNeg(self, p):
        return []

    @_('empty')
    def formulaAndNeg(self, p):
        return []        
    #####################################        

    @_('TRUE')
    def formulaAtomica(self, p):
        return ('true')

    @_('FALSE')
    def formulaAtomica(self, p):
        return ('false')

    @_('LPAREN formulaImpOrAndNeg RPAREN')
    def formulaNeg(self, p):
        return p.formulaImpOrAndNeg
        # return (p.formulaAndNeg[0], p.formulaAndNeg[1])
        # return '(' + p.formulaNeg[0] + p.formulaNeg[1] + ')'

    @_('empty')
    def formulaAtomica(self, p):
        return []

    @_('')
    def empty(self, p):
        return []

if __name__ == '__main__':
    data = '''
    -- ? (         not true )
    ? true imp false
'''
    lexer = CalcLexer()
    parser = CalcParser()
    # for tok in lexer.tokenize(data):
    #     print('type=%r, value=%r' % (tok.type, tok.value))
    print(json.dumps(parser.parse(lexer.tokenize(data))))
    # print(parser.parse(lexer.tokenize(data)))
