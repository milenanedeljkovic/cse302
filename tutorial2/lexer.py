import ply.lex as lex
import numpy as np


reserved = {"print": "PRINT", "def": "DEF", "main": "MAIN", "var": "VAR", "int": "INT"}
tokens = ("PLUS", "MINUS", "TIMES", "DIVIDE", "MODULUS",
          "BITWISEAND", "BITWISEOR", "BITWISEXOR", "SHL", "SHR",
          "SEMICOLON", "COLON",  "LPAREN", "RPAREN", "LBIGPAREN", "RBIGPAREN",
          "IDENT", "NUMBER", "EQUALS", "COMPLEMENT") + tuple(reserved.values())

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMICOLON = ';'
t_COLON = ":"
t_PLUS = r'\+'
t_MINUS = '-'
t_TIMES = '\*'
t_DIVIDE = '/'
t_MODULUS = "%"
t_BITWISEAND = '&'
t_BITWISEOR = '\|'
t_BITWISEXOR = '\^'
t_COMPLEMENT = '~'
t_SHL = "<<"
t_SHR = ">>"
t_EQUALS = "="
t_LBIGPAREN = '\{'
t_RBIGPAREN = '\}'

def t_IDENT(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, "IDENT")
    return t


def t_NUMBER(t):
    r'0|([1-9][0-9]*)'
    t.value = int(t.value)
    if t.value < - (1 << 63) or t.value > (1 << 63) - 1:
        print(f"Number out of bounds in line {t.lineno}")
    return t


def t_error(t):
    print(f"Illegal character ’{t.value[0]}’ on line {t.lexer.lineno}")
    t.lexer.skip(1) # skip one character


t_ignore = ' \t\f\v'


def t_newline(t):
    r'\n'
    t.lexer.lineno += 1
    # no return, signifying ignore


lexer = lex.lex()
# This will use Python introspection (reflection) to find out all the
# ‘tokens’ and ‘t_stuff’ in this module and create a suitable lexer from it