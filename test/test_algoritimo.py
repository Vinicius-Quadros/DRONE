import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import pandas as pd
from algoritimo import AlgoritmoGenetico

# Configuração de dados fictícios para o teste
coordenadas_data = {
    'cep': ['82821020', '82821111', '82821222'],
    'latitude': [-25.4284, -25.4294, -25.4304],
    'longitude': [-49.2733, -49.2743, -49.2753]
}
coordenadas = pd.DataFrame(coordenadas_data)
vento_previsao = {
    1: {'06:00:00': {'velocidade': 10, 'angulo': 90}, '09:00:00': {'velocidade': 5, 'angulo': 180}},
    2: {'06:00:00': {'velocidade': 15, 'angulo': 270}, '09:00:00': {'velocidade': 20, 'angulo': 0}},
    # Adicione mais dias e horários conforme necessário para os testes
}
populacao_tamanho = 2
geracoes = 3
velocidade_base = 50

# Instância do algoritmo genético para usar nos testes
algoritmo = AlgoritmoGenetico(coordenadas, populacao_tamanho, geracoes, velocidade_base, vento_previsao)


# Teste para gera_populacao_inicial
def test_gera_populacao_inicial():
    populacao = algoritmo.gera_populacao_inicial()
    assert len(populacao) == populacao_tamanho
    assert all(pop[0] == coordenadas_data['cep'][0] for pop in populacao)  # Começa com o CEP da UniBrasil
    assert all(pop[-1] == coordenadas_data['cep'][0] for pop in populacao)  # Termina com o CEP da UniBrasil


# Teste para calcula_fitness
def test_calcula_fitness():
    rota = ['82821020', '82821111', '82821020']  # Uma rota de exemplo
    fitness = algoritmo.calcula_fitness(rota)
    assert isinstance(fitness, float)
    assert fitness > 0  # Espera-se um valor de fitness positivo


# Teste para obtem_previsao_vento
def test_obtem_previsao_vento():
    dia, hora_formatada = algoritmo.obtem_previsao_vento(1, 21600)  # 06:00:00 em segundos
    assert dia == 1
    assert hora_formatada == '06:00:00'

    dia, hora_formatada = algoritmo.obtem_previsao_vento(1, 36000)  # 10:00:00 em segundos
    assert dia == 1
    assert hora_formatada == '09:00:00'  # Deveria arredondar para 09:00:00


# Teste para cruzamento
def test_cruzamento():
    pai1 = ['82821020', '82821111', '82821222', '82821020']
    pai2 = ['82821020', '82821222', '82821111', '82821020']
    filho = algoritmo.cruzamento(pai1, pai2)
    assert filho[0] == pai1[0]  # Início na UniBrasil
    assert filho[-1] == pai1[-1]  # Final na UniBrasil
    assert len(filho) == len(pai1)  # Mantém o tamanho


# Teste para mutacao
def test_mutacao():
    individuo = ['82821020', '82821111', '82821222', '82821020']
    individuo_copia = individuo.copy()
    algoritmo.mutacao(individuo)
    assert individuo != individuo_copia  # Deve haver uma alteração
    assert individuo[0] == individuo_copia[0]  # Início permanece o mesmo
    assert individuo[-1] == individuo_copia[-1]  # Final permanece o mesmo


# Teste para evoluir
def test_evoluir():
    melhor_rota, melhor_fitness = algoritmo.evoluir()
    assert isinstance(melhor_rota, list)
    assert melhor_rota[0] == coordenadas_data['cep'][0]  # Começa com o CEP da UniBrasil
    assert melhor_rota[-1] == coordenadas_data['cep'][0]  # Termina com o CEP da UniBrasil
    assert isinstance(melhor_fitness, float)
    assert melhor_fitness > 0

# Configuração de dados fictícios para o teste
coordenadas_data = {
    'cep': ['82821020', '82821111', '82821222'],
    'latitude': [-25.4284, -25.4294, -25.4304],
    'longitude': [-49.2733, -49.2743, -49.2753]
}
coordenadas = pd.DataFrame(coordenadas_data)
vento_previsao = {
    1: {'06:00:00': {'velocidade': 10, 'angulo': 90}, '09:00:00': {'velocidade': 5, 'angulo': 180}},
    2: {'06:00:00': {'velocidade': 15, 'angulo': 270}, '09:00:00': {'velocidade': 20, 'angulo': 0}},
    # Adicione mais dias e horários conforme necessário para os testes
}
populacao_tamanho = 2
geracoes = 3
velocidade_base = 50

# Instância do algoritmo genético para usar nos testes
algoritmo = AlgoritmoGenetico(coordenadas, populacao_tamanho, geracoes, velocidade_base, vento_previsao)

# Teste para gerar_csv_solucao
def test_gerar_csv_solucao():
    # Define uma rota que não termina na UniBrasil para verificar o ajuste no final
    melhor_rota = ['82821020', '82821111', '82821222']  # Rota de exemplo que não termina na UniBrasil
    nome_arquivo = 'solucao_teste.csv'  # Nome do arquivo CSV temporário

    # Gerar o CSV
    algoritmo.gerar_csv_solucao(melhor_rota, nome_arquivo)

    # Verificar se o arquivo foi criado
    assert os.path.exists(nome_arquivo)

    # Ler o arquivo CSV gerado e verificar seu conteúdo
    with open(nome_arquivo, 'r', encoding='utf-8') as file:
        linhas = file.readlines()
        assert len(linhas) > 1  # Deve ter pelo menos um cabeçalho e uma linha de dados

        # Verificar cabeçalho
        cabeçalho = linhas[0].strip().split(',')
        campos_esperados = ['CEP inicial', 'Latitude inicial', 'Longitude inicial', 'Dia do voo',
                            'Hora inicial', 'Velocidade', 'CEP final', 'Latitude final', 'Longitude final',
                            'Pouso', 'Hora final']
        assert cabeçalho == campos_esperados

        # Verificar que a rota inicial e final correspondem à UniBrasil
        primeira_linha = linhas[1].strip().split(',')
        ultima_linha = linhas[-1].strip().split(',')
        assert primeira_linha[0] == '82821020'  # CEP inicial na primeira linha (UniBrasil)
        assert ultima_linha[6] == '82821020'    # CEP final na última linha (UniBrasil)

        # Verificar se o loop parou no 5º dia
        for linha in linhas[1:]:
            dia_do_voo = int(linha.split(',')[3])  # Obtém o valor do 'Dia do voo'
            assert dia_do_voo <= 5  # Certifica-se de que o dia não ultrapassa 5

    # Remover o arquivo CSV temporário após o teste
    os.remove(nome_arquivo)

def test_calcula_fitness_rota_invalida():
    rota_invalida = ['82821111', '82821222', '82821020']  # Não começa na UniBrasil
    fitness = algoritmo.calcula_fitness(rota_invalida)
    assert fitness == float('inf')  # Deve retornar penalidade máxima

    rota_invalida = ['82821020', '82821111', '82821222']  # Não termina na UniBrasil
    fitness = algoritmo.calcula_fitness(rota_invalida)
    assert fitness == float('inf')  # Deve retornar penalidade máxima


# Teste para verificação de recarga e ajuste de tempo
def test_calcula_fitness_recarga_bateria():
    # Define uma rota simples que requer recarga de bateria
    rota = ['82821020', '82821111', '82821222', '82821020']



if __name__ == "__main__":
    pytest.main()
