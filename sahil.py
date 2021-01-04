#########################################################################
#                     SAHIL PROGRAMMING LANGUAGE                        #
#                    author : Abdulbasit Rubeiyya                       #
#########################################################################

#########################################################################
#                               IMPORTS                                 #
#                                                                       #
#########################################################################

from string_pointer import *

#########################################################################
#                             CONSTANTS                                 #
#                                                                       #
#########################################################################

DIGITS = '0123456789'

#########################################################################
#                               ERRORS                                  #
#                                                                       #
#########################################################################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f'Faili {self.pos_start.fn}, mstari wa {self.pos_start.ln + 1}'
        result += '\n\n' + string_pointer(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result
    
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Tatizo : Tokeni', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'sintaksia batili', details)   


#########################################################################
#                          ELEMENTS POSITIONING                         #
#                                                                       #
#########################################################################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1 

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):                                                         #create the copy of Position
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#########################################################################
#                               TOKENS                                  #
#                                                                       #
#########################################################################

TT_INT      =   'Nam'
TT_FLOAT    =   'Des'
TT_PLUS     =   'Jum'
TT_MINUS    =   'Toa'
TT_MUL      =   'Zid'
TT_DIV      =   'Gaw'
TT_LPAREN   =   'LPAREN'
TT_RPAREN   =   'RPAREN'
TT_EOF      =   'MWISHO'


class Token:
        def __init__(self, type_, value=None, pos_start=None, pos_end=None):
            self.type = type_
            self.value = value

            if pos_start:
                self.pos_start = pos_start.copy()
                self.pos_end = pos_start.copy()
                self.pos_end.advance()

            if pos_end:
                self.pos_end = pos_end

        def __repr__(self):
            if self.value: return f'{self.type}:{self.value}'
            return f'{self.type}'

#########################################################################
#                              LEXER                                    #
#                                                                       #
#########################################################################

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)                            #Impementing Posiion
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)                                 #implementing position
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None #1

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':                                  #ignore tab and spaces
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "' ") #2

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''                                        #keeping track of integers
        dot_count = 0                                       #keeping track of decimals
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count ==1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
            
        if dot_count == 0:                                               #if there is no dot(.)
            return Token(TT_INT, int(num_str), pos_start, self.pos)      #convert the number into integer
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)  #conver the number into integer

#########################################################################
#                                NODES                                  #
#                                                                       #
#########################################################################

class NumberNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'

class BinOpNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

    def __repr__(self):
        return f'{self.op_tok}, {self.node}'

#########################################################################
#                             PARSE RESULT                              #
#                                                                       #
######################################################################### 

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
    
    def register(self, res):
        if isinstance(res, ParseResult):                    #check parse result
            if res.error: self.error = res.error            #if error exist, assign error to such error
            return res.node

        return res
        
    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

#########################################################################
#                                PARSER                                 #
#                                                                       #
#########################################################################

class Parser:
    def __init__(self, tokens):                             #this needs another look
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1 
        if self.tok_idx < len(self.tokens):                 #3
            self.current_tok = self.tokens[self.tok_idx]    #grab the token index
        return self.current_tok

    #---------------------------------------------------------------#
                     #the grammar rules implementation#

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:   #4
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Tokeni inayotarajiwa ni '+', '-', '*' au '/' : "
            ))

        return res

                #--------------------------------------------#
                                #parse loop#

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):                 #consider the unary operations
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))             #return a successful responce of a numbernode token

        elif tok.type == TT_LPAREN:                         
            res.register(self.advance())                    #consider the left parenthes on expression
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())                #consider the right parenthes on expression
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Tokeni inayotarajiwa ni ')' : "
                ))

        return res.failure(InvalidSyntaxError(              #if caught a wrong token return this error
            tok.pos_start, tok.pos_end,
            "Tokeni uliyotumia sio NAMBA(Nam) wala sio DESIMALI(Des): "
        ))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
        
                                #parse loop#
                #--------------------------------------------#

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())                           #generic function
        if res.error: return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())                      #generic function
            if res.error: return res
            left =BinOpNode(left, op_tok, right)

        return res.success(left)

                     #the grammar rules implementation#
    #---------------------------------------------------------------#

#########################################################################
#                                 RUN                                   #
#                                                                       #
#########################################################################

def run(fn, text):
    #generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    #generate AST
    parser = Parser(tokens)
    ast = parser.parse()

    return ast.node, ast.error


#########################################################################
#                               COMMENTS                                #
#                                                                       #
#########################################################################

#1 - setting the position of the character to where position of the character should not exceed the length of the text, at the end of text set the position to none.

#2 - returns the unxpected Token value

#3 - if the token index is within the range of the token index

#4 - if it is not there is no error but it is also not the end of file