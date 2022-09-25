class Expression:
    def __str__(self):
        return f'EXPRESSION'


class ExpressionVar(Expression):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f'VARIABLE: {self.name}'


class ExpressionInt(Expression):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f'INTEGER: {self.value}'


class ExpressionUniOp(Expression):
    def __init__(self, operator, argument):
        self.operator = operator
        self.argument = argument

    def __str__(self):
        return f'UNIOP: operator: {self.operator}, argument: {self.argument}'


class ExpressionBinOp(Expression):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left_argument = left
        self.right_argument = right

    def __str__(self):
        return f'BINOP: {self.left_argument} {self.operator} {str(self.right_argument)}'


class Statement:
    def __str__(self):
        return 'STATEMENT'


class StatementVarDecl(Statement):
    def __init__(self, name, var_type, init):
        self.name = name
        self.var_type = var_type
        self.init = init

    def __str__(self):
        return f'VARDECL: name: {self.name}, var_type: {self.var_type}, value: {self.init}'


class StatementAssign(Statement):
    def __init__(self, lvalue, rvalue):
        self.lvalue = lvalue
        self.rvalue = rvalue

    def __str__(self):
        return f'ASSIGNMENT: lvalue: {self.lvalue}, rvalue: {self.rvalue}'


class StatementPrint(Statement):
    def __init__(self, argument):
        self.argument = argument

    def __str__(self):
        return f'PRINT: argument: {self.argument}'


class Program():
    def __init__(self, stmts):
        self.stmts = stmts # a list of statements
