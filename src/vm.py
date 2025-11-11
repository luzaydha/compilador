# src/vm.py
self.code: List[Tuple] = []
self.call_stack: List[int] = []


def load(self, code: List[Tuple]):
self.code = code
self.ip = 0


def push(self, v):
self.stack.append(v)


def pop(self):
if not self.stack:
raise VMError('stack underflow')
return self.stack.pop()


def run(self):
while self.ip < len(self.code):
instr = self.code[self.ip]
op = instr[0]
# dispatch
if op == 'PUSH':
self.push(instr[1])
elif op == 'LOAD':
name = instr[1]
if name not in self.globals:
raise VMError(f"Undefined variable '{name}'")
self.push(self.globals[name])
elif op == 'STORE':
name = instr[1]
val = self.pop()
self.globals[name] = val
elif op == 'POP':
self.pop()
elif op == 'ADD':
b = self.pop(); a = self.pop(); self.push(a + b)
elif op == 'SUB':
b = self.pop(); a = self.pop(); self.push(a - b)
elif op == 'MUL':
b = self.pop(); a = self.pop(); self.push(a * b)
elif op == 'DIV':
b = self.pop(); a = self.pop(); self.push(a // b)
elif op == 'JMP':
self.ip = instr[1]
continue
elif op == 'JZ':
target = instr[1]
cond = self.pop()
if cond == 0:
self.ip = target
continue
elif op == 'CALL':
target = instr[1]
# push return address
self.call_stack.append(self.ip + 1)
self.ip = target
continue
elif op == 'RET':
if not self.call_stack:
return
self.ip = self.call_stack.pop()
continue
else:
raise VMError(f'Unknown op {op}')


self.ip += 1


def dump(self):
print('STACK:', self.stack)
print('GLOBALS:', self.globals)