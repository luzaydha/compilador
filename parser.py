# src/parser.py
if self.peek()[1] == 'else':
self.eat('else'); self.eat('{')
while self.peek()[1] != '}': else_body.append(self.parse_stmt())
self.eat('}')
return If(cond, then_body, else_body)


def parse_while(self):
self.eat('while')
self.eat('(')
cond = self.parse_expr()
self.eat(')')
self.eat('{')
body = []
while self.peek()[1] != '}': body.append(self.parse_stmt())
self.eat('}')
return While(cond, body)


def parse_funcdef(self):
self.eat('function')
name = self.eat()[1]
self.eat('(')
params = []
if self.peek()[1] != ')':
while True:
params.append(self.eat('ID')[1])
if self.peek()[1] == ',': self.eat(','); continue
break
self.eat(')')
self.eat('{')
body = []
while self.peek()[1] != '}': body.append(self.parse_stmt())
self.eat('}')
return FuncDef(name, params, body)


# expressions (same as earlier example)
def parse_expr(self):
node = self.parse_term()
while True:
t = self.peek()
if t[1] in ('+','-'):
op = self.eat()[1]
node = BinOp(op, node, self.parse_term())
else: break
return node


def parse_term(self):
node = self.parse_factor()
while True:
t = self.peek()
if t[1] in ('*','/'):
op = self.eat()[1]
node = BinOp(op, node, self.parse_factor())
else: break
return node


def parse_factor(self):
t = self.peek()
if t[0] == 'NUMBER':
return Num(int(self.eat()[1]))
if t[0] == 'ID':
# could be call
name = self.eat()[1]
if self.peek()[1] == '(':
self.eat('(')
args = []
if self.peek()[1] != ')':
while True:
args.append(self.parse_expr())
if self.peek()[1] == ',': self.eat(','); continue
break
self.eat(')')
return Call(name, args)
return Var(name)
if t[1] == '(':
self.eat('(')
node = self.parse_expr()
self.eat(')')
return node
raise SyntaxError('Unexpected token in factor: '+str(t))