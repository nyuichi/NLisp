from string import whitespace
from ast    import *
from itertools import dropwhile, takewhile

class Token(object):
    DOT              = 1
    QUOTE            = 2
    QUASIQUOTE       = 3
    UNQUOTE          = 4
    UNQUOTE_SPLICING = 5
    LPAREN           = 6
    RPAREN           = 7
    EOF              = 8

    STRING           = 9
    INTEGER          = 10
    RATIONAL         = 11
    REAL             = 12
    COMPLEX          = 13
    SYMBOL           = 14
    BOOLEAN          = 15

    TERMINAL = whitespace+"(),'"
    
    def __init__(self, kind, value=None):
        self.kind  = kind
        self.value = value


class Lexer:
    '''Do lexical analyzation for scheme source code'''

    def __init__(self, exp):
        self.exp = list(exp)

    def scan(self):
        if not self.exp:
            return Token(Token.EOF)

        ch = self.exp.pop(0)

        if ch.isspace():
            return self.scan()
        elif ch == '(':
            return Token(Token.LPAREN)
        elif ch == ')':
            return Token(Token.RPAREN)
        elif ch == '\'':
            return Token(Token.QUOTE)
        elif ch == '`':
            return Token(Token.QUASIQUOTE)
        elif ch == '.':
            return self.tokenize_dot()
        elif ch == ',':
            return self.tokenize_comma()
        elif ch == '"':
            return self.tokenize_string()
        elif ch == '#':
            return self.tokenize_sharp()
        else:
            return self.tokenize_atom(ch)

    def tokenize_dot(self):
        ch = self.exp[0]
        if ch in Token.TERMINAL:
            return Token(Token.DOT)
        else:
            return Token(Token.REAL, Real('.'+self.read_atom()))

    def tokenize_comma(self):
        ch = self.exp[0]
        if ch == '@':
            self.exp.pop(0)
            return Token(Token.UNQUOTE_SPLICING)
        else:
            return Token(Token.UNQUOTE)

    def tokenize_string(self):
        s = ''
        while True:
            ch = self.exp.pop(0)
            if ch == '"':
                break
            elif ch == '\\':
                ch = self.exp.pop(0)
            s += ch
        return Token(Token.STRING, s)

    def tokenize_sharp(self):
        ch = self.exp.pop(0)
        if ch == 't':
            return Token(Token.BOOLEAN, t)
        elif ch == 'f':
            return Token(Token.BOOLEAN, f)

    def tokenize_atom(self, ch):
        atom = ch+self.read_atom()
        try:
            return Token(Token.INTEGER, Integer(atom))
        except ValueError:
            try:
                return Token(Token.REAL, Real(atom))
            except ValueError:
                try:
                    return Token(Token.RATIONAL, Rational(atom))
                except ValueError:
                    try:
                        return Token(Token.COMPLEX, Complex(atom))
                    except:
                        return Token(Token.SYMBOL, Symbol(atom))

    def read_atom(self):
        f = lambda ch: ch not in Token.TERMINAL
        atom = ''.join(list(takewhile(f, self.exp)))
        self.exp = list(dropwhile(f, self.exp))
        return atom


class Parser:
    def __init__(self, data):
        self.lexer = Lexer(data)
        self.token = None
        self.move()

    def move(self):
        self.token = self.lexer.scan()

    def get_sexp(self):
        if self.token.kind in (Token.RPAREN, Token.DOT):
            raise Exception("syntax error")
        elif self.token.kind == Token.EOF:
            return eof
        elif self.token.kind == Token.LPAREN:
            self.move()
            return self.get_list()
        elif self.token.kind == Token.QUOTE:
            self.move()
            return self.expand_read_macro('quote')
        elif self.token.kind == Token.QUASIQUOTE:
            self.move()
            return self.expand_read_macro('quasiquote')
        elif self.token.kind == Token.UNQUOTE:
            self.move()
            return self.expand_read_macro('unquote')
        elif self.token.kind == Token.UNQUOTE_SPLICING:
            self.move()
            return self.expand_read_macro('unquote-splicing')
        else:
            atom = self.token
            self.move()
            return atom.value

    def get_list(self):
        if self.token.kind == Token.RPAREN:
            self.move()
            return nil

        cell = Cell()
        cell.car = self.get_sexp()

        if self.token.kind == Token.DOT:
            self.move()
            cell.cdr = self.get_sexp()
            self.move()  # RPAREN
        else:
            cell.cdr = self.get_list()

        return cell

    def expand_read_macro(self, macro):
        cell = Cell()
        cell.car = Symbol(macro)
        cell.cdr = Cell(self.get_sexp(), nil)
        return cell


def get_sexps(exp):
    parser = Parser(exp)
    while True:
        sexp = parser.get_sexp()
        if sexp is eof:
            break
        else:
            yield sexp
