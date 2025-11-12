# CORRIJA PARA ISSO:
from index import lexer, Parser, GeradorDeCodigo, StackVM, compilar_e_executar
import test_compilador 

# --- TESTES AUTOMATIZADOS ---
# Cada função é um "caso de teste"

def test_atribuicao_simples():
    """Testa se 'x = 10' resulta em {'x': 10}."""
    vm = StackVM() # Cria uma VM limpa para este teste
    codigo = "x = 10"
    
    # Executa o compilador sem imprimir (verbose=False)
    memoria = compilar_e_executar(codigo, vm, verbose=False)
    
    # 3. VERIFICA o resultado
    assert memoria['x'] == 10

def test_operacoes_basicas():
    """Testa se 'a = 5 + 2 * 3' calcula a precedência correta."""
    vm = StackVM()
    codigo = "a = 5 + 2 * 3" # 5 + 6 = 11
    memoria = compilar_e_executar(codigo, vm, verbose=False)
    
    assert memoria['a'] == 11

def test_operador_unario():
    """Testa se 'b = -10 * -2' funciona."""
    vm = StackVM()
    codigo = "b = -10 * -2" # 20
    memoria = compilar_e_executar(codigo, vm, verbose=False)
    
    assert memoria['b'] == 20

def test_estado_persistente():
    """Testa se a VM mantém a memória entre execuções."""
    vm = StackVM() # Cria a VM uma vez
    
    # 1ª execução
    memoria = compilar_e_executar("x = 100", vm, verbose=False)
    assert memoria['x'] == 100
    
    # 2ª execução (usando a MESMA VM)
    memoria_depois = compilar_e_executar("y = x + 5", vm, verbose=False)
    
    # Verifica se os valores novos e antigos existem
    assert memoria_depois['x'] == 100
    assert memoria_depois['y'] == 105

def test_precedencia_com_parenteses():
    """Testa se z = (2 + 3) * 4 calcula 20, e não 14."""
    vm = StackVM()
    codigo = "z = (2 + 3) * 4"
    memoria = compilar_e_executar(codigo, vm, verbose=False)

    # 5 * 4 = 20
    assert memoria['z'] == 20

    # Teste bônus no mesmo caso
    codigo_2 = "w = 2 + (3 * 4)"
    memoria_2 = compilar_e_executar(codigo_2, vm, verbose=False)

    # 2 + 12 = 14
    assert memoria_2['w'] == 14