from fractions import Fraction
import re
import traceback
import sys

nil = type('Nil', (), {'__str__': lambda self: '()'})()
undef = type('Undef', (), {'__str__': lambda self: '#<undef>'})()
f = type('F', (), {'__str__': lambda self: '#f'})()
t = type('T', (), {'__str__': lambda self: '#t'})()
eof = type('Eof', (), {})

class Cell:

    def __init__(self, car=nil, cdr=nil):
        self.car = car
        self.cdr = cdr

    def __str__(self):
        s = '(' + str(self.car)
        cell = self.cdr
        while not cell == nil:
            if isinstance(cell, Cell):
                s += ' ' + str(cell.car)
                cell = cell.cdr
            else:
                s += ' . {0}'.format(cell)
                break
        return s+')'

    def __eq__(self, x):
        if x is nil:
            return self.car is nil and self.cdr is nil
        elif isinstance(x, Cell):
            return self.car == x.car and self.cdr == x.cdr
        else:
            return False
    
class Symbol:

    def __init__(self, exp):
        self.exp = exp

    def __str__(self):
        return self.exp

    def __eq__(self, x):
        return self.exp == x

    def __hash__(self):
        return hash(self.exp)

class Syntax:

    def __init__(self, proc):
        self.proc = proc

    def __str__(self):
        return '#<syntax>'

class Primitive:

    def __init__(self, proc):
        self.proc = proc

    def __str__(self):
        return '#<primitive>'

class Closure:

    def __init__(self, exp, pars, env):
        self.exp = exp
        self.pars = pars
        self.env = env

    def __str__(self):
        return '#<closure {0}>'.format(self.exp)

class Macro:

    def __init__(self, closure):
        self.closure = closure

    def __str__(self):
        return '#<macro {0}>'.format(self.closure.exp)

def intconverter(f):
    def conv(*args):
        t = getattr(Fraction, f.__name__)(*args)
        if t.denominator == 1:
            return Integer(t.numerator)
        else:
            return t
    return conv

def compconverter(f):
    def conv(*args):
        t = getattr(complex, f.__name__)(*args)
        if t.imag == 0:
            return Real(t.real)
        else:
            return t
    return conv

class Integer(int):

    def __div__(self, x):
        return Rational(self, x)

    def __str__(self):
        #return '#<integer {0}>'.format(int.__str__(self))
        return int.__str__(self)

class Real(float):

    def __str__(self):
        #return '#<real {0}>'.format(float.__str__(self))
        return float.__str__(self)


class Rational(Fraction):

    @intconverter
    def __new__(cls, x): pass
    @intconverter
    def __add__(self, x): pass
    @intconverter
    def __div__(self, x): pass
    @intconverter
    def __divmod__(self, x): pass
    @intconverter
    def __floordiv__(self, x): pass
    @intconverter
    def __mod__(self, x): pass
    @intconverter
    def __mul__(self, x): pass
    @intconverter
    def __pow__(self, x): pass
    @intconverter
    def __sub__(self, x): pass
    @intconverter
    def __radd__(self, x): pass
    @intconverter
    def __rdiv__(self, x): pass
    @intconverter
    def __rdivmod__(self, x): pass
    @intconverter
    def __rfloordiv__(self, x): pass
    @intconverter
    def __rmod__(self, x): pass
    @intconverter
    def __rmul__(self, x): pass
    @intconverter
    def __rpow__(self, x): pass
    @intconverter
    def __rsub__(self, x): pass

    def __str__(self):
        return '#<rational {0}/{1}>'.format(self.numerator, self.denominator)

class Complex(complex):

    def __new__(cls, x):
        n = r'[0-9]*(\.[0-9]*)?'
        m = re.compile('(([\-\+]?{0}))?((\-|\+){0})i'.format(n)).match(x)
        if m is not None:
            g = m.groups()
            c = complex.__new__(cls, float(g[1] or 0), float(g[3]))
            return c if c.imag != 0 else Real(c.real)
        else:
            raise ValueError

    @compconverter
    def __add__(self, x): pass
    @compconverter
    def __div__(self, x): pass
    @compconverter
    def __divmod__(self, x): pass
    @compconverter
    def __floordiv__(self, x): pass
    @compconverter
    def __mod__(self, x): pass
    @compconverter
    def __mul__(self, x): pass
    @compconverter
    def __pow__(self, x): pass
    @compconverter
    def __sub__(self, x): pass
    @compconverter
    def __radd__(self, x): pass
    @compconverter
    def __rdiv__(self, x): pass
    @compconverter
    def __rdivmod__(self, x): pass
    @compconverter
    def __rfloordiv__(self, x): pass
    @compconverter
    def __rmod__(self, x): pass
    @compconverter
    def __rmul__(self, x): pass
    @compconverter
    def __rpow__(self, x): pass
    @compconverter
    def __rsub__(self, x): pass

    def __str__(self):
        im = str(self.imag) if self.imag < 0 else '+'+str(self.imag)
        return '#<complex {0}{1}i>'.format(self.real, im)



