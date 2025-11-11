# src/codegen_vm.py
from ast import *


class CodeGenVM:
def __init__(self):
self.code = []


def emit(self, instr):
self.code.append(instr)


def gen_expr(self, node):
if isinstance(node, Num):
self.emit(('PUSH', node.value))
elif isinstance(node, Var):
self.emit(('LOAD', node.name))
elif isinstance(node, BinOp):
self.gen_expr(node.left); self.gen_expr(node.right)
opmap = {'+':'ADD','-':'SUB','*':'MUL','/':'DIV'}
self.emit((opmap[node.op],))
elif isinstance(node, Call):
# naive: assume function address will be resolved; we emit CALL with label index placeholder
for a in node.args: self.gen_expr(a)
self.emit(('CALL', node.name))
else:
raise RuntimeError('Unknown expr ' + str(node))


def gen_stmt(self, stmt):
if isinstance(stmt, Assign):
self.gen_expr(stmt.expr)
self.emit(('STORE', stmt.name))
elif isinstance(stmt, ExprStmt):
self.gen_expr(stmt.expr)
self.emit(('POP',))
elif isinstance(stmt, If):
self.gen_expr(stmt.cond)
# JZ to else or end
jz_pos = len(self.code); self.emit(('JZ', None))
for s in stmt.then_body: self.gen_stmt(s)
jmp_after_then_pos = len(self.code); self.emit(('JMP', None))
# patch JZ to point to else start
else_start = len(self.code)
self.code[jz_pos] = ('JZ', else_start)
for s in stmt.else_body: self.gen_stmt(s)
end = len(self.code)
self.code[jmp_after_then_pos] = ('JMP', end)
elif isinstance(stmt, While):
loop_start = len(self.code)
self.gen_expr(stmt.con