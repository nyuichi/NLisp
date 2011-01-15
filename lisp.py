#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, traceback
from ast import *
import analyzer
from evaluator import evals
from env import Env

isa = isinstance

def add_global_functions(env):
    add_syntaxes(env)
    add_primitive_functions(env)
    add_standard_functions(env)

def add_syntaxes(env):
    def quote_syntax(arg, env):
        return arg.car

    def if_syntax(arg, env):
        if evals(arg.car, env) == t:
            return evals(arg.cdr.car, env)
        elif not arg.cdr.cdr == nil:
            return evals(arg.cdr.cdr.car, env)
        
    def setq_syntax(arg, env):
        var = arg.car
        exp = arg.cdr.car
        if var in env:
            env[var] = evals(exp, env)
            return env[var]
        else:
            raise Exception('Symbol:{0} is not binded before'.format(var))

    def define_syntax(arg, env):
        var = arg.car
        exp = arg.cdr.car
        
        if isa(var, Cell):
            name = var.car
            pars = var.cdr
            env[name] = Closure(exp, pars, env)
        else:
            name = var
            env[name] = evals(exp, env)
        return name
        
    def lambda_syntax(arg, env):
        pars = arg.car
        exp = arg.cdr.car
        return Closure(exp, pars, env)

    def begin_syntax(arg, env):
        inner = Env(env)
        exp = arg
        val = undef
        while not exp == nil:
            val = evals(exp.car, inner)
            exp = exp.cdr
        return val
    
    def define_macro_syntax(arg, env):
        var = arg.car
        exp = arg.cdr.car

        if isa(var, Cell):
            name = var.car
            pars = var.cdr
            proc = Closure(exp, pars, env)
            env[name] = Macro(proc)
        else:
            name = var
            env[name] = Macro(evals(exp, env))
        return undef

    def quasiquote_syntax(arg, env):
        def connect(a, b):
            if isa(a, Cell):
                return Cell(a.car, connect(a.cdr, b))
            elif a == nil:
                return b
            else:
                raise Exception('Improper quasiquote')

        def expand(x):
            if isa(x, Cell):
                if x.car == 'unquote':
                    return evals(x.cdr.car, env)
                elif isa(x.car, Cell) and x.car.car == 'unquote-splicing':
                    return connect(evals(x.car.cdr.car, env), expand(x.cdr))
                else:
                    return Cell(expand(x.car), expand(x.cdr))
            else:
                return x

        return expand(arg.car)

    syntaxes = {
        'quote': quote_syntax,
        'if': if_syntax,
        'set!': setq_syntax,
        'lambda': lambda_syntax,
        'define': define_syntax,
        'begin': begin_syntax,
        'define-macro': define_macro_syntax,
        'quasiquote': quasiquote_syntax,
        }

    for name, cont in syntaxes.items():
        env[Symbol(name)] = Syntax(cont)

def add_primitive_functions(env):
    import operator as op
    funcs = {
        'cons': lambda x,y=nil: Cell(x,y),
        'car': lambda x: x.car,
        'cdr': lambda x: x.cdr,
        '+': lambda *args: reduce(op.add, args),
        '-': lambda *args: reduce(op.sub, args),
        '*': lambda *args: reduce(op.mul, args),
        '/': lambda *args: reduce(op.div, args),
        'mod': lambda x,y: t if x % y == 0 else f,
        'not': lambda x: f if x == t else t,
        '>': lambda x,y: t if x > y else f,
        '<': lambda x,y: t if x < y else f,
        '>=': lambda x,y: t if x >= y else f,
        '<=': lambda x,y: t if x <= y else f,
        '=': lambda x,y: t if x == y else f,
        'equal?': lambda x,y: t if x == y else f,
        'eq?': lambda x,y: t if x is y else f,
        'pair?': lambda x: t if isa(x, Cell) else f,
        'null?': lambda x: t if x == nil else f,
        'symbol?': lambda x: t if isa(x, Symbol) else f,
        'atom?': lambda x: t if not isa(x, Cell) else f,
        'display': lambda x: sys.stdout.write(str(x)) or undef,
        'newline': lambda: sys.stdout.write('\n') or undef,
        'quit': lambda: sys.stdout.write('Bye-bye!\n') or sys.exit(0),
        'exit': lambda: sys.stdout.write('Bye-bye!\n') or sys.exit(0),
        }

    for name, cont in funcs.items():
        env[Symbol(name)] = Primitive(cont)

def add_standard_functions(env):
    functions = '''
        (define (1+ x) (+ x 1))
        (define (1- x) (- x 1))
        (define (list . x) x)
        (define (cadr x) (car (cdr x)))
        (define (cdar x) (cdr (car x)))
        (define (caar x) (car (car x)))
        (define (cddr x) (cdr (cdr x)))

        (define (map f args)
          (if (null? args)
              '()
              (cons (f (car args)) (map f (cdr args)))))

        (define (filter f args)
          (if (null? args)
              '()
              (if (f (car args))
                  (cons (car args) (filter f (cdr args)))
                  (filter f (cdr args)))))
        
        (define-macro (let let-args . let-body)
          `((lambda ,(map car let-args) ,@let-body) ,@(map cadr let-args)))
        '''

    for exp in analyzer.get_sexps(functions):
        evals(exp, env)


def run_repl():
    print '////////////////////////////////////////////////////////////'
    print '// アメージング☆エターナルフォースブリザード☆わざびずLisp //'
    print '//////////////////// Powered by wasabi /////////////////////'
    print '////////////////////////////////////////////////////////////'
    print 'Type "(quit)" or "(exit)" to exit interactive mode'
    print 

    global_env = Env()
    add_global_functions(global_env)

    while True:
        s = raw_input('NLisp >> ')
        try:
            for exp in analyzer.get_sexps(s):
                result = evals(exp, global_env)
                if result:
                    print result
        except SystemExit:
            sys.exit(0)
        except SyntaxError:
            print 'Syntax Error!'
        except:
            print 'Rumtime Error!'
            print '-'*30
            traceback.print_exc(file=sys.stdout)
            print '-'*30


if __name__ == '__main__':
    run_repl()

