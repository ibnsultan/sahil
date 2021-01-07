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
        result += f'Faili: {self.pos_start.fn}, Mstari: {self.pos_start.ln + 1}'
        result += '\n' + string_pointer(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result
    
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Tokeni batili', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'sintaksia batili', details)

class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'RT batili', details)
        self.context = context
    
    def as_string(self):
        result  = self.generate_traceback()
        result += f'{self.error_name}: {self.details}'
        result += '\n' + string_pointer(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f'Faili: {pos.fn}, Mstari: {str(pos.ln + 1)}, katika: {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return 'Tafiti: kosa lilofanyika :\n' + result

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
TT_POW      =   'Kip'
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
            elif self.current_char == '^':
                tokens.append(Token(TT_POW, pos_start=self.pos))
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

		self.pos_start = self.tok.pos_start
		self.pos_end = self.tok.pos_end

	def __repr__(self):
		return f'{self.tok}'

class BinOpNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

		self.pos_start = self.left_node.pos_start
		self.pos_end = self.right_node.pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

		self.pos_start = self.op_tok.pos_start
		self.pos_end = node.pos_end

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'

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
                "Tokeni inayotarajiwa ni '+', '-', '*' au '/' : \n"
            ))

        return res

                #--------------------------------------------#
                                #parse loop#
    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
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
                    "Tokeni inayotarajiwa ni ')' : \n"
                ))

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Tokeni inayotarijiwa ni namba, desimali au opersheni ya hisabati"
        ))

    def power(self):
        return self.bin_op(self.atom, (TT_POW, ), self.factor)

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):                 #consider and preced the unary operations
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
        
                                #parse loop#
                #--------------------------------------------#

    def bin_op(self, func_a, ops, func_b=None):
        if func_b==None:
            func_b = func_a
        res = ParseResult()
        left = res.register(func_a())                           #generic function
        if res.error: return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func_b())                      #generic function
            if res.error: return res
            left =BinOpNode(left, op_tok, right)

        return res.success(left)

                     #the grammar rules implementation#
    #---------------------------------------------------------------#

#########################################################################
#                           RUNTIME RESULTS                             #
#                                                                       #
#########################################################################

class RTResult:
    def __init__(self):
        self.value = None
        self.error = None
    
    def register(self, res):
        if res.error: self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self

#########################################################################
#                                VALUES                                 #
#                                                                       #
#########################################################################

class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self
    
    def added_to(self, other):                                 #Implement addition
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def subbed_by(self, other):                                #Implement substraction
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None

    def multed_by(self, other):                                #Implement multiplication
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None

    def powed_by(self, other):                                #Implement power
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None

    def dived_by(self, other):                                 #Implement division
        if isinstance(other, Number):
            if other.value == 0:                               #handles number divide by zero
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'nambari gawanya kwa sifuri ni uhusiano batili : \n',
                    self.context
                )

            return Number(self.value / other.value).set_context(self.context), None

    def __repr__(self):
        return str(self.value)

#########################################################################
#                                CONTEXT                                #
#                                                                       #
#########################################################################

class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos

#########################################################################
#                              INTERPRETER                              #
#                                                                       #
#########################################################################

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} ya kupitia iliyofafanuliwa')

    #---------------------------------------------------------------#
              #defining a visit method for each node type#
    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))

        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == TT_POW:
            result, error = left.powed_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res

        error = None

        if node.op_tok.type == TT_MINUS:                            #how to deal with a negative number
            number, error = number.multed_by(Number(-1))

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

              #defining a visit method for each node type#
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
    if ast.error: return None, ast.error

    #Run Program
    interpreter = Interpreter()
    context = Context('<programu>')
    result = interpreter.visit(ast.node, context)


    return result.value, result.error


#########################################################################
#                               COMMENTS                                #
#                                                                       #
#########################################################################

#1 - setting the position of the character to where position of the character should not exceed the length of the text, at the end of text set the position to none.

#2 - returns the unxpected Token value

#3 - if the token index is within the range of the token index

#4 - if it is not there is no error but it is also not the end of file