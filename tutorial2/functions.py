import classes


def json_to_expr(js_obj):
    if js_obj[0] == '<expression:var>':
        return classes.ExpressionVar(js_obj[1]['name'][1]['value'])
    if js_obj[0] == '<expression:int>':
        return classes.ExpressionInt(js_obj[1]['value'])
    if js_obj[0] == '<expression:uniop>':
        operator = js_obj[1]['operator'][1]['value']
        argument = json_to_expr(js_obj[1]['argument'])  # recursive call
        return classes.ExpressionUniOp(operator, argument)
    if js_obj[0] == '<expression:binop>':
        operator = js_obj[1]['operator'][1]['value']
        left = json_to_expr(js_obj[1]['left'])
        right = json_to_expr(js_obj[1]['right'])
        return classes.ExpressionBinOp(operator, left, right)
    if js_obj[0] == "<expression:eval>":
        return json_to_expr(js_obj[1]["arguments"])
    if js_obj[0] == "<expression:call>":
        return json_to_expr(js_obj[1]['arguments'][0])
    raise ValueError(f'Unrecognized <expression>: {js_obj[0]}')


def json_to_stmt(js_obj):
    if js_obj[0] == '<statement:vardecl>':
        variable = classes.ExpressionVar(js_obj[1]['name'][1]['value'])
        var_type = js_obj[1]['type'][0]
        init = js_obj[1]['init'][1]['value']
        return classes.StatementVarDecl(variable, var_type, init)
    if js_obj[0] == '<statement:assign>':
        rvalue = json_to_expr(js_obj[1]['rvalue'])
        if js_obj[1]['lvalue'][0] == "<lvalue:var>":
            lvalue = classes.ExpressionVar(js_obj[1]['lvalue'][1]['name'][1]['value'])
            return classes.StatementAssign(lvalue, rvalue)
        raise ValueError(f'Unrecognized <lvalue>: {js_obj[1]["lvalue"][0]}')
    if js_obj[0] == "<statement:eval>":
        argument = json_to_expr(js_obj[1]["expression"])
        return classes.StatementPrint(argument)
    raise ValueError(f'Unrecognized <statement>: {js_obj[0]}')
