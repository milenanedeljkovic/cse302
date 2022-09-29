import functions
import classes
import json
import sys
import lexer
import parser

ops_dict = {"addition": "add", "subtraction": "sub", "multiplication": "mul", "division": "div",
            "modulus": "mod", "bitwise-xor": "xor", "bitwise-or": "or", "bitwise-and": "and",
            "opposite": "neg", "bitwise-negation": "not", "left-shift": "shl", "right-shift": "shr",
            "double-equals": "eqeq"}

temp_map = dict()


def expr_to_tac(expr, tac, counter, variables):
    if isinstance(expr, classes.ExpressionVar):
        if expr.name in variables:
            tac[0]["body"].append({"opcode": "copy", "args": [variables[expr.name]], "result": f'%{counter}'})
        else:
            variables[expr.name] = f'%{counter}'
            tac[0]["body"].append({"opcode": "copy", "args": [variables[expr.name]], "result": f'%{counter}'})
        counter += 1
    elif isinstance(expr, classes.ExpressionInt):
        tac[0]["body"].append({"opcode": "copy", "args": [expr.value], "result": f'%{counter}'})
        counter += 1
    elif isinstance(expr, classes.ExpressionUniOp):
        tac, counter, variables = expr_to_tac(expr.argument, tac, counter, variables)
        tac[0]["body"].append({"opcode": ops_dict[expr.operator], "args": [f'%{counter - 1}'], "result": f'%{counter}'})
        counter += 1
    elif isinstance(expr, classes.ExpressionBinOp):
        tac, counter, variables = expr_to_tac(expr.left_argument, tac, counter, variables)
        c = counter
        tac, counter, variables = expr_to_tac(expr.right_argument, tac, counter, variables)
        tac[0]["body"].append({"opcode": ops_dict[expr.operator], "args": [f'%{c - 1}, %{counter - 1}'], "result": f'%{counter}'})
        counter += 1
    return tac, counter, variables


def stmt_to_tac(stmt, tac, counter, variables):
    if isinstance(stmt, classes.StatementVarDecl):
        # in this tutorial variables are always initialized to a constant
        tac[0]["body"].append({"opcode": "copy", "args": [stmt.init], "result": f'%{counter}'})
        variables[stmt.variable.name] = f'%{counter}'
        counter += 1
    elif isinstance(stmt, classes.StatementAssign):
        # we assume that lvalue is a variable
        tac, counter, variables = expr_to_tac(stmt.rvalue, tac, counter, variables)
        if stmt.lvalue.name not in variables:
            print(f"Line {stmt.lineno}: Error: Assigning to a non-declared variable {stmt.lvalue.name}.")
        else:
            tac[0]["body"].append({"opcode": "copy", "args": [f'%{counter - 1}'], "result": f'{variables[stmt.lvalue.name]}'})
    elif isinstance(stmt, classes.StatementPrint):
        tac, counter, variables = expr_to_tac(stmt.argument, tac, counter, variables)
        tac[0]["body"].append({"opcode": "print", "args": [f'%{counter - 1}'], "result": None})
    return tac, counter, variables


def compiler(bx_file_path):
    """json_file is the .json file representing the BX program to compile
    The AST is in the 'ast' filed of the first json object in this file.
    For this tutorial, the whole program is written within a single function
    main() which takes no arguments."""
    # getting the AST
    with open(bx_file_path, 'r') as f:
        code = f.read()
    ast = parser.parser.parse(code, lexer=lexer.lexer)

    counter = 0  # to keep track of the first register that is surely free
    tac = [{"proc": "@main", "body": []}]

    for stmt in ast.stmts:
        tac, counter, variables = stmt_to_tac(stmt, tac, counter, variables)

    with open("tac_file.json", 'w') as f:
        json.dump(tac, f)

    print(variables)


bx_file = sys.argv[1]
compiler(bx_file)
