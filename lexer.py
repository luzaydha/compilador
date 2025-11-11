# src/lexer.py
import re


token_spec = [
('NUMBER', r'\d+'),
('ID', r'[A-Za-z_]\w*'),
('OP', r'[+\-*/=;(),{}]'),
('SKIP', r'[ \t\n]+'),
]
regex = '|'.join(f"(?P<{n}>{p})" for n,p in token_spec)


def tokenize(code):
for m in re.finditer(regex, code):
kind = m.lastgroup
val = m.group()
if kind == 'SKIP':
continue
yield (kind, val)