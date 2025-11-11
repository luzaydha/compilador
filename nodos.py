# src/ast.py
from dataclasses import dataclass


@dataclass
class Num: value: int
@dataclass
class Var: name: str
@dataclass
class BinOp: op: str; left: object; right: object
@dataclass
class Assign: name: str; expr: object
@dataclass
class ExprStmt: expr: object
@dataclass
class If: cond: object; then_body: list; else_body: list
@dataclass
class While: cond: object; body: list
@dataclass
class FuncDef: name: str; params: list; body: list
@dataclass
class Return: expr: object
@dataclass
class Call: name: str; args: list