import ply.yacc as yacc
from lexer import tokens
import classes

tokens = tokens
precedence = (('left', 'BITWISEOR'), ('left', 'BITWISEXOR'), ('left', 'BITWISEAND'), ('left', 'SHL', 'SHR'),
              ('left', 'PLUS', 'MINUS'), ('left', 'TIMES', 'DIVIDE'), ('left', 'MODULUS'),
              ('right', 'COMPLEMENT'), ('right', 'OPPOSITE'))


def p_expr_ident(p):
    """expr : IDENT"""
    p[0] = classes.ExpressionVar(p[1])


def p_expr_number(p):
    """expr : NUMBER"""
    p[0] = classes.ExpressionInt(int(p[1]))


def p_expr_parens(p):
    """expr : LPAREN expr RPAREN"""
    p[0] = p[2]


def p_expr_opposite(p):
    """expr : MINUS expr %prec OPPOSITE"""
    p[0] = classes.ExpressionUniOp("opposite", p[1])


def p_expr_complement(p):
    """expr : COMPLEMENT expr"""
    p[0] = classes.ExpressionUniOp("bitwise-negation", p[1])


def p_expr_plus(p):
    """expr : expr PLUS expr"""
    p[0] = classes.ExpressionBinOp("addition", p[1], p[3])


def p_expr_minus(p):
    """expr : expr MINUS expr"""
    p[0] = classes.ExpressionBinOp("subtraction", p[1], p[3])


def p_expr_times(p):
    """expr : expr TIMES expr"""
    p[0] = classes.ExpressionBinOp("multiplication", p[1], p[3])


def p_expr_divide(p):
    """expr : expr DIVIDE expr"""
    p[0] = classes.ExpressionBinOp("division", p[1], p[3])


def p_expr_mod(p):
    """expr : expr MODULUS expr"""
    p[0] = classes.ExpressionBinOp("modulus", p[1], p[3])


def p_expr_and(p):
    """expr : expr BITWISEAND expr"""
    p[0] = classes.ExpressionBinOp("bitwise-and", p[1], p[3])


def p_expr_or(p):
    """expr : expr BITWISEOR expr"""
    p[0] = classes.ExpressionBinOp("bitwise-or", p[1], p[3])


def p_expr_xor(p):
    """expr : expr BITWISEXOR expr"""
    p[0] = classes.ExpressionBinOp("bitwise-xor", p[1], p[3])


def p_expr_shl(p):
    """expr : expr SHL expr"""
    p[0] = classes.ExpressionBinOp("left-shift", p[1], p[3])


def p_expr_shr(p):
    """expr : expr SHR expr"""
    p[0] = classes.ExpressionBinOp("right-shift", p[1], p[3])


def p_stmt_decl(p):
    """stmt : VAR expr EQUALS expr COLON INT SEMICOLON"""
    if not(isinstance(p[2], classes.ExpressionVar)):
        print(f"Line {p.lineno}: Error: Assigning to an object that is not a variable.")
    p[0] = classes.StatementVarDecl(p[2], p[6], p[3], p.lineno)


def p_stmt_assign(p):
    """stmt : expr EQUALS expr SEMICOLON"""
    if not(isinstance(p[1], classes.ExpressionVar)):
        print(f"Assigning an expression that is not a variable at line {p.lineno}.")
    p[0] = classes.StatementAssign(p[1], p[3], p.lineno)


def p_stmt_print(p):
    """stmt : PRINT LPAREN expr RPAREN SEMICOLON"""
    p[0] = classes.StatementPrint(p[3], p.lineno)


def p_stmt_star(p):
    """stmt_star :
                | stmt_star stmt"""
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]
        p[0].append(p[2])


def p_program(p):
    """prog : DEF MAIN LPAREN RPAREN LBIGPAREN stmt_star RBIGPAREN"""
    p[0] = classes.Program(p[6])


def p_error(p):
    if p is None:
        print("Invalid program.")
    else:
        print(f'Line {p.lineno}: Error at: {p.value}')
        parser.errok()  # we'll still try to compile the code


parser = yacc.yacc(start='prog')
