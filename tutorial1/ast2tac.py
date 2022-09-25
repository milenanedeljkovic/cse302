import functions
import classes
import json
import sys

ops_dict = {"addition": "add", "substraction": "sub", "multiplication": "mul", "division": "div",
            "modulus": "mod", "bitwise-xor": "xor", "bitwise-or": "or", "bitwise-and": "and",
            "opposite": "neg", "bitwise-negation": "not", "left-shift": "shl", "right-shift": "shr",
            "double-equals": "eqeq"}


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
        variables[stmt.name] = f'%{counter}'
        counter += 1
    elif isinstance(stmt, classes.StatementAssign):
        # we assume that lvalue is a variable
        tac, counter, variables = expr_to_tac(stmt.rvalue, tac, counter, variables)
        if stmt.lvalue.name not in variables:
            print(f"Assigning a non-declared variable {stmt.lvalue.name}!")
        else:
            variables[stmt.lvalue.name] = f'%{counter}'
            tac[0]["body"].append({"opcode": "copy", "args": [f'%{counter - 1}'], "result": f'%{counter}'})
            counter += 1
    elif isinstance(stmt, classes.StatementPrint):
        tac, counter, variables = expr_to_tac(stmt.argument, tac, counter, variables)
        tac[0]["body"].append({"opcode": "print", "args": [f'%{counter - 1}'], "result": None})
    return tac, counter, variables


def compiler(json_file_path):
    """json_file is the .json file representing the BX program to compile
    The AST is in the 'ast' filed of the first json object in this file.
    For this tutorial, the whole program is written within a single function
    main() which takes no arguments."""
    # getting the AST
    with open(json_file_path, 'r') as fp:
        js_obj = json.load(fp)
    ast = js_obj["ast"][0][1]["body"]

    counter = 0  # to keep track of the first register that is surely free
    variables = dict()
    tac = [{"proc": "@main", "body": []}]

    for stmt in ast:
        stmt_obj = functions.json_to_stmt(stmt)
        print(stmt[0])
        tac, counter, variables = stmt_to_tac(stmt_obj, tac, counter, variables)

    with open("tac_file.json", 'w') as f:
        json.dump(tac, f)

    print(variables)


print(sys.argv)
json_file = sys.argv[1]
compiler(json_file)
