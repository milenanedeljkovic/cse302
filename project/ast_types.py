from copy import copy
from dataclasses import dataclass, field

from types import NoneType
from typing import Any, Dict, List, Optional
import json_constructors
import type_checking
from enum import Enum


# class BXTypes(Enum):
#     UNRESOLVED = -1
#     INT = 1
#     BOOL = 2
#     VOID = 3

class BXTypes:
    pass


@dataclass
class BXTypesInt(BXTypes):
    pass


@dataclass
class BXTypesBool(BXTypes):
    pass


@dataclass
class BXTypesVoid(BXTypes):
    pass


@dataclass
class BXTypesNull(BXTypes):
    pass


@dataclass
class BXTypesPointer(BXTypes):
    def __init__(self, ty: BXTypes):
        self.ty = ty


@dataclass
class BXTypesListType(BXTypes):
    def __init__(self, length: int, ty: BXTypes):
        self.length = length
        self.ty = ty


@dataclass
class StructField:
    def __init__(self, name: str, ty: BXTypes):
        self.name = name
        self.ty = ty


@dataclass
class BXTypesStruct(BXTypes):
    def __init__(self, fields: List[StructField]):
        self.fields = fields


class BXTypesUnresolved(BXTypes):
    pass



@dataclass
class ProcType:
    args_ty: List[BXTypes]
    return_ty: BXTypes

    def __hash__(self) -> int:
        return hash(tuple(self.args_ty + [self.return_ty]))


RESERVED_FUNCTIONS = {"bx_print_int": ProcType([BXTypesInt], BXTypesVoid),
                      "bx_print_bool": ProcType([BXTypesBool()], BXTypesVoid)}

########## LValue ##########


@ dataclass
class LValue:
    symbol: str
    lineno: int

    @ classmethod
    def from_node(cls, node: dict):
        return json_constructors.lvalue_constructor(node)


@ dataclass
class LValueVar(LValue):
    pass

    def __repr__(self):
        return self.symbol

########## Expressions ##########


@ dataclass
class Expression:
    lineno: int

    def __init__(self):
        self.ty: BXTypes = BXTypesUnresolved
        self.block: Optional['StatementBlock'] = None

    @ classmethod
    def from_node(cls, node: dict):
        return json_constructors.expression_constructor(node)


@ dataclass
class Param(Expression):
    symbol: str

    def __post_init__(self):
        super().__init__()

    @ classmethod
    def from_node(cls, node: dict):
        pass

    def __repr__(self) -> str:
        return f"{self.symbol} : {self.ty}"


@ dataclass
class ExpressionVar(Expression):
    symbol: str

    def __post_init__(self):
        super().__init__()

    def __repr__(self):
        return self.symbol


@ dataclass
class ExpressionUniOp(Expression):
    op: str
    argument: Expression

    def __post_init__(self):
        super().__init__()

    def __repr__(self):
        return f"{self.op}({self.argument})"


@ dataclass
class ExpressionBinOp(Expression):
    op: str
    left: Expression
    right: Expression

    def __post_init__(self):
        super().__init__()

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"


@ dataclass
class ExpressionCall(Expression):
    target: str
    args: List[Expression]

    def __post_init__(self):
        super().__init__()

    def __repr__(self):
        return f"{self.target}({', '.join(str(arg) for arg in self.args)})"


@ dataclass
class ExpressionInt(Expression):
    value: int
    ty: BXTypes = BXTypesInt()

    def __repr__(self) -> str:
        return f"{self.value}"


@ dataclass
class ExpressionBool(Expression):
    value: bool
    ty: BXTypes = BXTypesBool()

    def __repr__(self) -> str:
        return f"{self.value}"


@dataclass
class ExpressionAccess(Expression):  # either index access of a list, or access by . or ->
    obj: Expression

@dataclass
class ExpressionAccessIndex(ExpressionAccess):
    index: Expression

    def __repr__(self):
        return f"{self.obj}[{self.index}]"


@dataclass
class ExpressionAccessPoint(ExpressionAccess):
    index: ExpressionVar

    def __repr__(self):
        return f"{self.obj}.{self.index}"


@dataclass
class ExpressionAccessArrow(ExpressionAccess):
    index: ExpressionVar
    def __repr__(self):
        return f"{self.obj}->{self.index}"

@dataclass
class ExpressionAddress(Expression):
    obj: Expression

    def __repr__(self):
        return f"&{self.obj}"


@dataclass
class ExpressionDeref(Expression):
    obj: Expression

    def __repr__(self):
        return f"*{self.obj}"
########## Statements ##########


@ dataclass
class Statement:
    lineno: int

    @ classmethod
    def from_node(cls, node: dict):
        return json_constructors.statement_constructor(node)


@dataclass
class SymbolRecord:
    ty: BXTypes
    temp: Optional[str] = None


@ dataclass
class StatementBlock(Statement):
    statements: List[Statement]
    proc_scope: Dict[str, List[ProcType]] = field(default_factory=dict)
    scopes: List[Dict[str, SymbolRecord]] = field(default_factory=lambda: [{}])

    def inherit_scopes(self, child: 'StatementBlock'):
        child.scopes = self.scopes.copy() + [{}]
        child.proc_scope = self.proc_scope

    def define_type(self, symbol: str, ty: BXTypes):
        assert symbol not in self.scopes[-1], f"Symbol {symbol} already defined in this scope."
        self.scopes[-1][symbol] = SymbolRecord(ty)

    def define_temp(self, symbol: str, temp: str, global_def=False):
        if global_def:
            self.scopes[0][symbol].temp = temp
        else:
            record = self.get_record(symbol)
            assert record.temp is None, f"Temporary for the symbol {symbol} is already set."
            record.temp = temp

    def get_record(self, symbol: str) -> SymbolRecord:
        for scope in reversed(self.scopes):
            if symbol in scope:
                return scope[symbol]
        raise Exception(f"Error on line {self.lineno}: Symbol {symbol} not defined.")

    def get_type(self, symbol: str) -> BXTypes:
        return self.get_record(symbol).ty

    def get_temp(self, symbol: str) -> str:
        temp = self.get_record(symbol).temp
        assert temp is not None, f"Temporary for the symbol {symbol} is not set."
        return temp

    def define_proc(self, name: str, proc_type: ProcType):
        # Function polymorphism
        if name in self.proc_scope:
            for signature in self.proc_scope[name]:
                if len(proc_type.args_ty) == len(signature.args_ty):
                    for param_i in range(len(proc_type.args_ty)):
                        if proc_type.args_ty[param_i] != signature.args_ty[param_i]:
                            break
                    else:
                        raise TypeError(f"Function {name} is already defined.")
            else:
                self.proc_scope[name].append(proc_type)
        else:
            self.proc_scope[name] = [proc_type]

    def recognize_proc(self, symbol: str, args: List[BXTypes]) -> ProcType:
        if symbol not in self.proc_scope:
            raise Exception(f"Symbol {symbol} not defined.")
        for proc in self.proc_scope[symbol]:
            if proc.args_ty == args:
                return proc
        raise Exception(f"Symbol {symbol} not defined with args {args}.")

    def __repr__(self) -> str:
        return '\n'.join(repr(stmt) for stmt in self.statements)


@ dataclass
class StatementVarDecl(Statement):
    vars: List[ExpressionVar]
    rvalues: List[Expression]
    typehint: BXTypes
    block: Optional[StatementBlock] = None

    def __repr__(self):
        return f"var {', '.join(str(var) for var in self.vars)} = {self.rvalues}"


@dataclass
class StatementTyDecl(Statement):
    var: ExpressionVar
    ty: BXTypes


@ dataclass
class StatementAssign(Statement):
    lvalue: LValue
    rvalue: Expression
    block: Optional[StatementBlock] = None

    def __repr__(self):
        return f"{self.lvalue} = {self.rvalue};"


@ dataclass
class StatementEval(Statement):
    call: ExpressionCall
    block: Optional[StatementBlock] = None

    def __repr__(self):
        return f"{self.call};"


@ dataclass
class StatementIfElse(Statement):
    condition: Expression
    body: StatementBlock
    optelse: Optional[StatementBlock]
    block: Optional[StatementBlock] = None

    def __repr__(self):
        if self.optelse is None:
            return f"if ({self.condition})" + " {\n" + repr(self.body) + "\n}"
        else:
            return f"if ({self.condition})" + " {\n" + repr(self.body) + "\n}" + "else" + "{\n" + repr(self.optelse) + "\n}"


@ dataclass
class StatementWhile(Statement):
    condition: Expression
    body: StatementBlock
    block: Optional[StatementBlock] = None

    def __repr__(self):
        return f"while ({self.condition})" + " {\n" + repr(self.body) + "\n}"


@ dataclass
class StatementJump(Statement):
    jump: str

    def __repr__(self):
        return f"{self.jump};"


@ dataclass
class StatementReturn(Statement):
    return_expr: Optional[Expression] = None
    block: Optional[StatementBlock] = None

    def __repr__(self) -> str:
        return f"return {self.return_expr};"

########## Procedure ##########


@ dataclass
class ControlStacks:
    break_stack: List[int] = field(default_factory=list)
    continue_stack: List[int] = field(default_factory=list)


@ dataclass
class Procedure:
    name: str
    params: List[Param]
    block: StatementBlock
    lineno: int
    return_ty: BXTypes = BXTypesVoid
    control_stacks: ControlStacks = field(default_factory=ControlStacks)

    def __post_init__(self):
        param_names = [param.symbol for param in self.params]
        if len(param_names) != len(set(param_names)):
            raise ValueError("Procedure has double parameters.")

    @ classmethod
    def from_node(cls, node: dict):
        return json_constructors.procedure_constructor(node)

    def __repr__(self) -> str:
        return f"{self.name}({self.params}) -> {self.return_ty}" + " {\n" + repr(self.block) + "\n}"


########## Program ##########


@ dataclass
class Program:
    procedures: List[Procedure]
    global_block: StatementBlock
    lineno: int

    def __post_init__(self):
        # check that there is exactly one main
        main_count = sum(1 for proc in self.procedures if proc.name == "main")
        assert main_count == 1, "There must be exactly one main procedure."

    @ classmethod
    def from_node(cls, node: dict):
        return json_constructors.program_constructor(node)

    def resolve(self):
        line = type_checking.program_resolver(self)
        return line

    def __repr__(self):
        return "\n\n".join(repr(proc) for proc in self.procedures)
