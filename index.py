import re

# --- Fase 1: O LEXER (Analisador Léxico) ---
# O Lexer transforma a string de entrada em uma lista de "tokens".

class Token:
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor
    def __repr__(self):
        return f"Token({self.tipo}, {repr(self.valor)})"

# Tipos de tokens que nossa linguagem reconhece
TOKENS = [
    ('NUMERO',    r'\d+'),
    ('ID',        r'[a-zA-Z_][a-zA-Z0-9_]*'), # Nomes de variáveis
    ('IGUAL',     r'='),
    ('MAIS',      r'\+'),
    ('MENOS',     r'-'),
    ('MULT',      r'\*'),
    ('DIV',       r'/'),
    ('PAREN_ESQ', r'\('),
    ('PAREN_DIR', r'\)'),
    ('ESPACO',    r'\s+'), # Ignoramos espaços
    ('ERRO',      r'.'),    # Qualquer outro caractere é um erro
]

# Compila os padrões de regex em uma única expressão
padrao_tokens = '|'.join(f'(?P<{nome}>{regex})' for nome, regex in TOKENS)
token_regex = re.compile(padrao_tokens)

def lexer(codigo):
    tokens = []
    for match in token_regex.finditer(codigo):
        tipo = match.lastgroup
        valor = match.group()

        if tipo == 'ESPACO':
            continue # Ignora espaços em branco
        elif tipo == 'ERRO':
            raise ValueError(f"Caractere inesperado: {valor}")
        
        # Converte números para o tipo int
        if tipo == 'NUMERO':
            valor = int(valor)

        tokens.append(Token(tipo, valor))
    return tokens

# --- Fase 2: A AST (Nós da Árvore Sintática) ---
# Estas são as "peças" que o Parser vai usar para construir a árvore.

class NoNumero:
    def __init__(self, token):
        self.valor = token.valor
    def __repr__(self):
        return f"Num({self.valor})"

class NoVariavel:
    def __init__(self, token):
        self.nome = token.valor
    def __repr__(self):
        return f"Var({self.nome})"

class NoOperacaoBinaria:
    def __init__(self, esq, op, dir):
        self.esq = esq
        self.op = op # O token do operador
        self.dir = dir
    def __repr__(self):
        return f"Op({self.esq}, {self.op.tipo}, {self.dir})"

class NoAtribuicao:
    def __init__(self, var_token, expr):
        self.var_nome = var_token.valor
        self.expr = expr # A expressão à direita do '='
    def __repr__(self):
        return f"Atrib(Var({self.var_nome}), {self.expr})"

# NOVO NÓ para a AST
class NoOperacaoUnaria:
    def __init__(self, op, expr):
        self.op = op # O token (MAIS ou MENOS)
        self.expr = expr # A expressão que está sendo negada/positivada
    def __repr__(self):
        return f"UnaryOp({self.op.tipo}, {self.expr})"
        
# --- Fase 3: O PARSER (Analisador Sintático) ---
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def token_atual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None # Fim dos tokens

    def avancar(self):
        self.pos += 1

    def consumir(self, tipo_esperado):
        token = self.token_atual()
        if token and token.tipo == tipo_esperado:
            self.avancar()
            return token
        raise SyntaxError(f"Esperado token {tipo_esperado}, mas encontrou {token.tipo if token else 'FIM'}")

    # A gramática da nossa linguagem (simplificada):
    #
    # programa   ::= lista_de_comandos
    # comando    ::= atribuicao | expressao
    # atribuicao ::= ID IGUAL expressao
    # expressao  ::= termo ( (MAIS | MENOS) termo )*
    # termo      ::= fator ( (MULT | DIV) fator )*
    # fator      ::= NUMERO | ID | PAREN_ESQ expressao PAREN_DIR
    
    def parse(self):
        # Um programa é uma lista de comandos (atribuições ou expressões)
        comandos = []
        while self.token_atual():
            comandos.append(self.parse_comando())
        return comandos

    def parse_comando(self):
        # Um comando pode ser uma atribuição ou apenas uma expressão
        token_um = self.tokens[self.pos]
        # "Lookahead": Espiamos o *próximo* token
        token_dois = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None

        if token_um.tipo == 'ID' and token_dois and token_dois.tipo == 'IGUAL':
            return self.parse_atribuicao()
        else:
            return self.parse_expressao()

    def parse_atribuicao(self):
        var_token = self.consumir('ID')
        self.consumir('IGUAL')
        expr = self.parse_expressao()
        return NoAtribuicao(var_token, expr)

    def parse_expressao(self):
        no = self.parse_termo()

        while self.token_atual() and self.token_atual().tipo in ('MAIS', 'MENOS'):
            op = self.token_atual()
            self.avancar()
            no = NoOperacaoBinaria(no, op, self.parse_termo())
        return no

    def parse_termo(self):
        no = self.parse_fator()

        while self.token_atual() and self.token_atual().tipo in ('MULT', 'DIV'):
            op = self.token_atual()
            self.avancar()
            no = NoOperacaoBinaria(no, op, self.parse_fator())
        return no

    def parse_fator(self):
        token = self.token_atual()

        if token.tipo in ('MAIS', 'MENOS'):
            self.avancar() 
            op = token
            expr = self.parse_fator() 
            return NoOperacaoUnaria(op, expr)

        if token.tipo == 'NUMERO':
            self.avancar()
            return NoNumero(token)
        
        elif token.tipo == 'ID':
            self.avancar()
            return NoVariavel(token)

        elif token.tipo == 'PAREN_ESQ':
            self.avancar()
            no = self.parse_expressao() 
            self.consumir('PAREN_DIR')
            return no
        
        raise SyntaxError(f"Fator inesperado: {token}")

# --- Fase 4: O GERADOR DE CÓDIGO ---

class GeradorDeCodigo:
    def __init__(self):
        self.instrucoes = []

    def gerar(self, ast_comandos):
        self.instrucoes = []
        for comando in ast_comandos:
            self.visitar(comando)
        return self.instrucoes

    def visitar(self, no):
        # O nome do método é baseado no tipo do nó
        metodo = f'visitar_{type(no).__name__}'
        visitante = getattr(self, metodo, self.visitar_generico)
        return visitante(no)

    def visitar_generico(self, no):
        raise TypeError(f"Nenhum método 'visitar' para o nó {type(no).__name__}")

    def visitar_NoNumero(self, no):
        # Instrução: Coloca o número na pilha
        self.instrucoes.append(('push', no.valor))

    def visitar_NoVariavel(self, no):
        # Instrução: Carrega o valor da variável para a pilha
        self.instrucoes.append(('load', no.nome))

    def visitar_NoOperacaoBinaria(self, no):
        # 1. Gera código para o lado esquerdo (resultado vai para a pilha)
        self.visitar(no.esq)
        # 2. Gera código para o lado direito (resultado vai para a pilha)
        self.visitar(no.dir)
        
        # 3. A pilha agora tem [..., valor_esq, valor_dir]
        #    Aplica a operação
        if no.op.tipo == 'MAIS':
            self.instrucoes.append(('add', None))
        elif no.op.tipo == 'MENOS':
            self.instrucoes.append(('sub', None))
        elif no.op.tipo == 'MULT':
            self.instrucoes.append(('mul', None))
        elif no.op.tipo == 'DIV':
            self.instrucoes.append(('div', None))

    def visitar_NoAtribuicao(self, no):
        # 1. Gera o código para a expressão (resultado vai para a pilha)
        self.visitar(no.expr)
        # 2. Instrução: Armazena o valor do topo da pilha na variável
        self.instrucoes.append(('store', no.var_nome))

    def visitar_NoOperacaoUnaria(self, no):
        if no.op.tipo == 'MENOS':
            # Implementa "-expr" como "0 - expr"
            self.instrucoes.append(('push', 0)) # 1. Empilha 0
            self.visitar(no.expr)               # 2. Empilha o valor da expressão
            self.instrucoes.append(('sub', None))  # 3. Subtrai (pilha: [valor_expr, 0] -> sub -> [0 - valor_expr])
        
        elif no.op.tipo == 'MAIS':
            # Implementa "+expr", que é só "expr"
            # Não faz nada além de visitar a expressão interna
            self.visitar(no.expr)

# --- (BÔNUS) Fase 5: A MÁQUINA VIRTUAL DE PILHA ---
# Um interpretador simples para o nosso "bytecode"

class StackVM:
    def __init__(self):
        self.stack = []
        self.memory = {} # Onde as variáveis são armazenadas

    def executar(self, instrucoes):
        self.stack = []
        # self.memory = {} # Descomente para resetar a memória a cada execução
        
        for (opcode, arg) in instrucoes:
            if opcode == 'push':
                self.stack.append(arg)
            elif opcode == 'load':
                valor = self.memory.get(arg)
                if valor is None:
                    raise ValueError(f"Variável '{arg}' não definida.")
                self.stack.append(valor)
            elif opcode == 'store':
                valor = self.stack.pop()
                self.memory[arg] = valor
            else:
                # Operações binárias
                if len(self.stack) < 2:
                    raise ValueError("Stack underflow! Operação binária precisa de 2 operandos.")
                dir = self.stack.pop()
                esq = self.stack.pop()
                
                if opcode == 'add':
                    self.stack.append(esq + dir)
                elif opcode == 'sub':
                    self.stack.append(esq - dir)
                elif opcode == 'mul':
                    self.stack.append(esq * dir)
                elif opcode == 'div':
                    # Divisão de inteiros
                    self.stack.append(esq // dir)
        
        return self.stack, self.memory

# --- JUNTANDO TUDO ---

def compilar_e_executar(codigo):
    print("--- COMPILADOR TOY ---")
    print(f"Código Fonte:\n{codigo}\n")

    # Fase 1: Lexer
    tokens = lexer(codigo)
    print(f"Tokens: \n{tokens}\n")

    # Fase 2 & 3: Parser e AST
    parser = Parser(tokens)
    ast = parser.parse()
    print(f"AST (Árvore Sintática Abstrata): \n{ast}\n")

    # Fase 4: Gerador de Código
    gerador = GeradorDeCodigo()
    instrucoes = gerador.gerar(ast)
    print(f"Instruções da VM (Bytecode):")
    for inst in instrucoes:
        print(f"  {inst}")
    print("\n")

    # Fase 5: Execução na VM
    print("--- Executando VM ---")
    vm = StackVM()
    pilha_final, memoria_final = vm.executar(instrucoes)
    
    print(f"Memória Final: {memoria_final}")
    print(f"Pilha Final: {pilha_final}")
    print("-" * 22)


# --- Exemplo de Uso ---

# Programa 1
programa = """
x = 10
y = 20
z = x + y * 2
"""
compilar_e_executar(programa) # Memória: {'x': 10, 'y': 20, 'z': 50}

# Programa 2 (continua a memória)
programa2 = "w = (x + 5) * z"
compilar_e_executar(programa2) # Memória: {'x': 10, 'y': 20, 'z': 50, 'w': 750}

# --- NOVO TESTE ---
# Programa 3: Testando o operador unário
print("\n=== TESTE UNÁRIO ===")
programa3 = """
a = -10
b = -a + 5
c = 10 * -b
"""
compilar_e_executar(programa3)

