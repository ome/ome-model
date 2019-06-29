# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2009 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://genshi.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://genshi.edgewall.org/log/.

"""Various Python version compatibility classes and functions."""


import sys
from types import CodeType
import six

# We need to test if an object is an instance of a string type in places

def isstring(obj):
    return isinstance(obj, str)

# We need to differentiate between StringIO and BytesIO in places

from io import StringIO, BytesIO


# We want to test bytestring input to some stuff.

def wrapped_bytes(bstr):
    assert bstr.startswith('b')
    return bstr


# We do some scary stuff with CodeType() in template/eval.py

def get_code_params(code):
    return (code.co_nlocals, code.co_kwonlyargcount, code.co_stacksize,
            code.co_flags, code.co_code, code.co_consts, code.co_names,
            code.co_varnames, code.co_filename, code.co_name,
            code.co_firstlineno, code.co_lnotab, (), ())

def build_code_chunk(code, filename, name, lineno):
    return CodeType(0, code.co_nlocals, code.co_kwonlyargcount,
                    code.co_stacksize, code.co_flags | 0x0040,
                    code.co_code, code.co_consts, code.co_names,
                    code.co_varnames, filename, name, lineno,
                    code.co_lnotab, (), ())
