from types import NoneType
from typing import List
import ast_types
from bxscanner import tokens
import py.ply.yacc as yacc  # type: ignore

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'BINOR'),
    ('left', 'XOR'),
    ('left', 'BINAND'),
    ('nonassoc', 'EQ', 'NEQ'),
    ('nonassoc', 'LT', 'LTE', 'GT', 'GTE'),
    ("left", "LBITSHIFT", "RBITSHIFT"),
    ("left", "PLUS", "MINUS"),
    ("left", "STAR", "SLASH", "PERCENT"),
    ("right", "UMINUS", "NOT"),
    ("right", "BINNEG"),
    ("left", "ADDR", "DEREF", "LSPAREN")

)


binOps = {'+': 'addition', '-': 'substraction', '*': 'multiplication', '/': 'division', '&': 'bitwise-and',
          '|': 'bitwise-or', '^': 'bitwise-xor', '%': 'modulus', '>>': 'bitwise-shift-right',
          '<<': 'bitwise-shift-left',
          "==": 'is-equal', "!=": 'is-not-equal', "<": 'is-less-than', ">": 'is-greater-than',
          "<=": 'is-less-than-or-equal', ">=": 'is-greater-than-or-equal',
          "&&": 'logical-and', "||": 'logical-or', }

uniOps = {'-': 'opposite', '~': 'bitwise-negation', '!': 'logical-negation'}

# p_ignore = r" \t\f\v"


def p_error(p):
    if p is None:
        raise SyntaxError("Syntax error at EOF.")
    else:
        raise SyntaxError(f"Error on line {p.lineno}: Syntax error at {p.value[0]}.")


def p_empty(p):
    """empty :
             | COMMENT"""
    pass


def p_expr_number(p):
    """expr : NUM"""
    num = int(p[1])
    if not -2**31 <= num <= 2**31 - 1:
        raise ValueError(f"Number {num} on line {p.lexer.lineno} is out of range.")
    p[0] = ast_types.ExpressionInt(value=num, lineno=p.lexer.lineno)


def p_expr_bool(p):
    """expr : TRUE
            | FALSE"""
    p[0] = ast_types.ExpressionBool(value=(p[1] == 'true'), lineno=p.lexer.lineno)


def p_expr_brackets(p):
    """expr : LPAREN expr RPAREN"""
    p[0] = p[2]


def p_expr_uniop(p):
    """expr : MINUS expr %prec UMINUS
            | BINNEG expr
            | NOT expr"""
    p[0] = ast_types.ExpressionUniOp(op=uniOps[p[1]], argument=p[2], lineno=p.lexer.lineno)


def p_expr_binop(p):
    """expr : expr PLUS expr
            | expr MINUS expr
            | expr STAR expr
            | expr SLASH expr
            | expr LBITSHIFT expr
            | expr RBITSHIFT expr
            | expr PERCENT expr
            | expr AND expr
            | expr OR expr
            | expr BINAND expr
            | expr BINOR expr
            | expr XOR expr
            | expr EQ expr
            | expr NEQ expr
            | expr LT expr
            | expr GT expr
            | expr LTE expr
            | expr GTE expr"""
    p[0] = ast_types.ExpressionBinOp(op=binOps[p[2]], left=p[1], right=p[3], lineno=p.lexer.lineno)


def p_other_inline_param(p):
    """other_inline_param : empty
                          | other_inline_param COMMA IDENT EQUALS expr"""
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[1]
        p[0].append((ast_types.ExpressionVar(symbol=p[3], lineno = p.lexer.lineno), p[5]))


def p_inline_param_block(p):
    """inline_param_block : empty
                          | IDENT EQUALS expr other_inline_param"""
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = [(p[1], p[3])] + p[4]


def p_exprstar(p):
    """expr : IDENT LPAREN inline_param_block RPAREN"""
    p[0] = ast_types.ExpressionCall(target=p[1], args=p[3], lineno=p.lexer.lineno)


def p_assignable(p):
    """assignable : IDENT
                    | STAR expr %prec DEREF
                    | expr LSPAREN expr RSPAREN
                    | expr POINT IDENT
                    | expr ARROW IDENT"""
    if len(p) == 2:
        p[0] = ast_types.ExpressionVar(symbol=p[1], lineno=p.lexer.lineno)
    elif p[1] == '*':
        p[0] = ast_types.ExpressionDeref(obj=p[2], lineno=p.lexer.lineno)
    elif p[2] == '[':
        p[0] = ast_types.ExpressionAccessIndex(obj=p[1], index=p[3], lineno=p.lexer.lineno)
    elif p[2] == '.':
        p[0] = ast_types.ExpressionAccessPoint(obj=p[1], index=ast_types.ExpressionVar(symbol=p[3], lineno=p.lexer.lineno), lineno=p.lexer.lineno)
    elif p[2] == '->':
        p[0] = ast_types.ExpressionAccessArrow(obj=p[1], index=ast_types.ExpressionVar(symbol=p[3], lineno=p.lexer.lineno), lineno=p.lexer.lineno)
    else:
        raise NotImplementedError(f"Unknown assignable expression {p} in line {p.lexer.lineno}")

def p_expr_assignable(p):
    """expr : assignable
            | BINAND assignable %prec ADDR"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ast_types.ExpressionAddress(obj=p[2], lineno=p.lexer.lineno)

def p_expr_null(p):
    """expr : NULL"""
    p[0] = ast_types.BXTypesNull()


def p_ty(p):
    """ty : INT
            | BOOL
            | VOID
            | STRUCT LCPAREN structfield structfieldstar RCPAREN
            | ty LSPAREN NUM RSPAREN
            | ty STAR %prec DEREF"""
    if p[1] == 'int':
        p[0] = ast_types.BXTypesInt()
    elif p[1] == 'bool':
        p[0] = ast_types.BXTypesBool()
    elif p[1] == "void":
        p[0] = ast_types.BXTypesVoid()
    elif p[1] == "struct":
        p[0] = ast_types.BXTypesStruct(fields=[p[3]] + p[4])
    elif isinstance(p[1], ast_types.BXTypes):
        if len(p) == 3:
            p[0] = ast_types.BXTypesPointer(ty=p[1])
        elif len(p) == 4:
            p[0] = ast_types.BXTypesListType(length=p[3], ty=p[1])
    else:
        raise ValueError("Unknown type.")


def p_stmt_vardecl(p):
    """stmt_vardecl : VARDECL inline_param_block COLON ty SEMICOLON"""
    p[0] = ast_types.StatementVarDecl(vars=[var[0] for var in p[2]], rvalues=[value[1] for value in p[2]], typehint=p[4], lineno=p.lexer.lineno)


def p_stmt_tydecl(p):
    """stmt_tydecl : TYPE expr EQUALS ty SEMICOLON"""
    if not isinstance(p[2], ast_types.ExpressionVar):
        raise TypeError(f"Cannot assign type to expression {p[2]} in line {p.lineno}.")
    else:
        p[0] = ast_types.StatementTyDecl(var=p[2], ty=p[4], lineno=p.lexer.lineno)


def p_stmt_eval(p):
    """stmt_eval : expr SEMICOLON"""
    p[0] = ast_types.StatementEval(call=p[1], lineno=p.lexer.lineno)


def p_ifelse(p):
    """ifelse : IF LPAREN expr RPAREN block optelse"""
    p[0] = ast_types.StatementIfElse(condition=p[3], body=p[5], optelse=p[6], lineno=p.lexer.lineno)


def p_optelse(p):
    """optelse : empty
               | ELSE block
               | ELSE ifelse"""
    if len(p) == 2:
        p[0] = None
    elif isinstance(p[2], ast_types.StatementBlock):
        p[0] = p[2]
    else:
        p[0] = ast_types.StatementBlock(statements=[p[2]], lineno=p.lexer.lineno)


def p_while(p):
    """while : WHILE LPAREN expr RPAREN block"""
    p[0] = ast_types.StatementWhile(condition=p[3], body=p[5], lineno=p.lexer.lineno)


def p_jump(p):
    """jump : BREAK SEMICOLON
            | CONTINUE SEMICOLON"""
    p[0] = ast_types.StatementJump(jump=p[1], lineno=p.lexer.lineno)


def p_return(p):
    """return : RETURN expr SEMICOLON
              | RETURN SEMICOLON"""
    if len(p) == 4:
        p[0] = ast_types.StatementReturn(return_expr=p[2], lineno=p.lexer.lineno)
    else:
        p[0] = ast_types.StatementReturn(lineno=p.lexer.lineno)


def p_block(p):
    """block : LCPAREN stmtstar RCPAREN"""
    p[0] = ast_types.StatementBlock(statements=p[2], lineno=p.lexer.lineno)


def p_stmt_assign(p):
    """stmt_assign : IDENT EQUALS expr SEMICOLON"""
    p[0] = ast_types.StatementAssign(lvalue=ast_types.LValueVar(
        symbol=p[1], lineno=p.lexer.lineno), rvalue=p[3], lineno=p.lexer.lineno)


def p_stmt(p):
    """stmt : stmt_vardecl
            | stmt_assign
            | stmt_tydecl
            | stmt_eval
            | ifelse
            | while
            | jump
            | return
            | block"""
    p[0] = p[1]


def p_stmts(p):
    """stmtstar : empty
                | stmtstar stmt"""
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[1]
        if isinstance(p[2], list):
            p[0] += p[2]
        else:
            p[0].append(p[2])


def p_proc_ty(p):
    """ proc_ty : empty
                  | COLON ty"""
    if len(p) == 2:
        p[0] = ast_types.BXTypesVoid()
    else:
        p[0] = p[2]


def p_other_param(p):
    """other_param : empty
                   | COMMA IDENT other_param """
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = [ast_types.Param(symbol=p[2], lineno=p.lexer.lineno)] + p[3]


def p_param(p):
    """param : IDENT other_param COLON ty """
    untyped_params = [ast_types.Param(symbol=p[1], lineno=p.lexer.lineno)] + p[2]
    for param in untyped_params:
        param.ty = p[4]
    p[0] = untyped_params


def p_other_param_block(p):
    """other_param_block : empty
                         | COMMA param other_param_block"""
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[2] + p[3]


def p_param_block(p):
    """param_block : empty
                   | param other_param_block"""
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[1] + p[2]


def p_procedure(p):
    """procedure : DEF IDENT LPAREN param_block RPAREN proc_ty block"""
    p[0] = ast_types.Procedure(name=p[2], params=p[4], return_ty=p[6], block=p[7], lineno=p.lexer.lineno)


def p_decl(p):
    """decl : procedure
            | stmt_vardecl
            | stmt_tydecl"""
    p[0] = p[1]


def p_declstar(p):
    """ declstar : empty
                 | declstar decl"""
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[1]
        p[0].append(p[2])

def p_structfield(p):
    """structfield : expr COLON ty"""
    if not isinstance(p[1], ast_types.ExpressionVar):
        raise TypeError(f"Name of a struct field cannot be expression {p[1]} in line {p.lineno}")
    else:
        p[0] = ast_types.StructField(name=p[1].symbol, ty=p[3])
        

def p_structfieldstar(p):
    """structfieldstar : empty
                 | COMMA structfield structfieldstar"""
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[3]
        p[0].append(p[2])
    


def p_program(p):
    """program : declstar"""
    global_decl: List[ast_types.StatementVarDecl] = []
    procedures: List[ast_types.Procedure] = []

    for decl in p[1]:
        if isinstance(decl, ast_types.Procedure):
            procedures.append(decl)
        elif isinstance(decl, ast_types.StatementVarDecl):
            global_decl.append(decl)
        else:
            raise ValueError("Unknown declaration type.")

    global_block = ast_types.StatementBlock(statements=global_decl, lineno=p.lexer.lineno)
    p[0] = ast_types.Program(procedures=procedures,
                             global_block=global_block, lineno=p.lexer.lineno)


def create_parser():
    parser = yacc.yacc(start='program')
    return parser


create_parser()
