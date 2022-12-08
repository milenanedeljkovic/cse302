# type: ignore
import py.ply.lex as lex


reserved = {"def": "DEF", "var": "VARDECL", "int": "INT", "bool": "BOOL", "true": "TRUE", "false": "FALSE",
            "if": "IF", "else": "ELSE", "while": "WHILE", "break": "BREAK", "continue": "CONTINUE", "return": "RETURN",
            "type": "TYPE", "void": "VOID", "struct": "STRUCT", "null": "NULL"}
tokens = ('PLUS', 'MINUS', 'STAR', 'SLASH', 'PERCENT', 'AND', 'OR', 'XOR', 'LBITSHIFT', 'RBITSHIFT', 'BINNEG', 'LPAREN',
          'RPAREN', 'LCPAREN', 'RCPAREN', 'COLON', 'COMMA', 'EQUALS', 'SEMICOLON', 'NUM', 'IDENT', 'COMMENT',
          'NOT', 'LT', 'GT', 'LTE', 'GTE', 'EQ', 'NEQ', 'BINAND', 'BINOR', 'LSPAREN', 'RSPAREN', 'POINT', 'ARROW'
          ) + tuple(reserved.values())

t_INT = r"int"
t_PLUS = r"\+"
t_MINUS = r"-"
t_SEMICOLON = r";"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LCPAREN = r"\{"
t_RCPAREN = r"\}"
t_LSPAREN = r"\["
t_RSPAREN = r"\]"
t_EQUALS = r"="
t_LBITSHIFT = r"<<"
t_RBITSHIFT = r">>"
t_AND = r"&&"
t_BINAND = r"&"
t_OR = r"\|\|"
t_BINOR = r"\|"
t_XOR = r"\^"
t_PERCENT = r"%"
t_COLON = r":"
t_COMMA = r","
t_SLASH = r"/"
t_STAR = r"\*"
t_BINNEG = r"~"
t_DEF = r"def"
t_VARDECL = r"var"
t_NOT = r"!"
t_LT = r"<"
t_GT = r">"
t_LTE = r"<="
t_GTE = r">="
t_EQ = r"=="
t_NEQ = r"!="
t_BOOL = r"bool"
t_TRUE = r"true"
t_FALSE = r"false"
t_IF = r"if"
t_ELSE = r"else"
t_WHILE = r"while"
t_BREAK = r"break"
t_CONTINUE = r"continue"
t_RETURN = r"return"
t_POINT = r"\."
t_ARROW = r"->"


def t_NUM(t):
    r"0|-?[1-9][0-9]*"
    t.type = reserved.get(t.value, "NUM")
    return t


def t_COMMENT(t):
    r"//.*"


def t_IDENT(t):
    r"[A-Za-z_][A-Za-z0-9_]*"
    t.type = reserved.get(t.value, "IDENT")
    return t


def t_error(t):
    line = t.lexer.lexdata.splitlines()[t.lexer.lineno - 1]
    underline = " " * (t.lexpos - line.rfind("\t", 0, t.lexpos)) + "^"
    print(f"Illegal character {t.value[0]} at line {t.lexer.lineno}: \n {line}\n {underline}")
    raise SyntaxError(f"Illegal character {t.value[0]}.")  # skip one character


t_ignore = " \t\f\v"


def t_newline(t):
    r"\n"
    t.lexer.lineno += 1

def create_lexer() -> lex.Lexer:
    return lex.lex()
