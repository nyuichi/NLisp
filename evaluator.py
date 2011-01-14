#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ast import *
from env import Env
import analyzer

isa = isinstance

def issymbol(x):
    return isa(x, Symbol)

def islist(x):
    return isa(x, Cell)

def isconstant(x):
    for n in Integer, Real, Rational, Complex, str:
        if isa(x,n): return True
    else:
        return x in (t, f, nil)

def bind(pars, args, env):
    if isa(pars, Cell):
        env[pars.car] = args.car
        bind(pars.cdr, args.cdr, env)
    elif not pars == nil:
        env[pars] = args
    elif args != nil:
        raise Exception("Invalid number of arguments")

def evalall(exps, env):
    if exps == nil:
        return nil
    else:
        return Cell(evals(exps.car, env), evalall(exps.cdr, env))

def evals(x, env):
    if x is eof:
        return

    elif issymbol(x):
        return env.find(x)

    elif islist(x):
        proc = evals(x.car, env)

        if isconstant(proc):
            return proc

        elif isa(proc, Syntax):
            return proc.proc(x.cdr, env)

        elif isa(proc, Primitive):
            args, elem = [], x.cdr
            while not elem == nil:
                args.append(evals(elem.car, env))
                elem = elem.cdr
            return proc.proc(*args)

        elif isa(proc, Closure):
            # Evaluate parameters
            new_scope = Env(proc.env)
            arguments = evalall(x.cdr, new_scope)
            # Bind
            bind(proc.pars, arguments, new_scope)
            # Evaluate a closure
            return evals(proc.exp, new_scope)

        elif isa(proc, Macro):
            new_scope = Env(proc.closure.env)
            # Bind
            bind(proc.closure.pars, x.cdr, new_scope)
            # Expand
            exp = evals(proc.closure.exp, new_scope)
            # Evaluate
            return evals(exp, env)

        else:
            raise Exception('Not callable: {0},{1}'.format(type(x.car), x.car))

    elif isconstant(x):
        return x
