import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
import pandas as pd
from algoritimo import AlgoritmoGenetico, verifica_arquivo_solucao
from previsao import vento_previsao

coordenadas_data = {
    'cep': ['82821020', '82821111', '82821222'],
    'latitude': [-25.4284, -25.4294, -25.4304],
    'longitude': [-49.2733, -49.2743, -49.2753]
}
coordenadas = pd.DataFrame(coordenadas_data)
populacao_tamanho = 2
geracoes = 3
velocidade_base = 50
algoritmo = AlgoritmoGenetico(coordenadas, populacao_tamanho, geracoes, velocidade_base, vento_previsao)

def test_gera_populacao_inicial():
    populacao = algoritmo.gera_populacao_inicial()
    assert len(populacao) == populacao_tamanho
    assert all(pop[0] == coordenadas_data['cep'][0] for pop in populacao)
    assert all(pop[-1] == coordenadas_data['cep'][0] for pop in populacao)

def test_calcula_fitness():
    rota = ['82821020', '82821111', '82821020']
    fitness = algoritmo.calcula_fitness(rota)
    assert isinstance(fitness, float)
    assert fitness > 0

def test_calcula_fitness_bateria_e_horario():
    coordenadas_data = {
        'cep': ['82821020', '82821111', '82821222', '82821020'],
        'latitude': [-25.4284, -25.4294, -25.4304, -25.4284],
        'longitude': [-49.2733, -49.2743, -49.2753, -49.2733]
    }
    coordenadas = pd.DataFrame(coordenadas_data)
    vento_previsao = {
        1: {'06:00:00': {'velocidade': 10, 'angulo': 90}, '09:00:00': {'velocidade': 5, 'angulo': 180}},
        2: {'06:00:00': {'velocidade': 15, 'angulo': 270}, '09:00:00': {'velocidade': 20, 'angulo': 0}},
    }
    algoritmo = AlgoritmoGenetico(coordenadas, populacao_tamanho=2, geracoes=2, velocidade_base=30, vento_previsao=vento_previsao)
    rota = ['82821020', '82821111', '82821222', '82821020'] * 10  # Repetida para simular uma rota extensa
    fitness = algoritmo.calcula_fitness(rota)
    assert isinstance(fitness, float)
    assert fitness > 0

def test_obtem_previsao_vento():
    dia, hora_formatada = algoritmo.obtem_previsao_vento(1, 21600)
    assert dia == 1
    assert hora_formatada == '06:00:00'

    dia, hora_formatada = algoritmo.obtem_previsao_vento(1, 36000)
    assert dia == 1
    assert hora_formatada == '09:00:00'

def test_cruzamento():
    pai1 = ['82821020', '82821111', '82821222', '82821020']
    pai2 = ['82821020', '82821222', '82821111', '82821020']
    filho = algoritmo.cruzamento(pai1, pai2)
    assert filho[0] == pai1[0]
    assert filho[-1] == pai1[-1]
    assert len(filho) == len(pai1)

def test_mutacao():
    individuo = ['82821020', '82821111', '82821222', '82821020']
    individuo_copia = individuo.copy()
    algoritmo.mutacao(individuo)
    assert individuo != individuo_copia
    assert individuo[0] == individuo_copia[0]
    assert individuo[-1] == individuo_copia[-1]


# Teste para evoluir
def test_evoluir():
    melhor_rota, melhor_fitness = algoritmo.evoluir()
    assert isinstance(melhor_rota, list)
    assert melhor_rota[0] == coordenadas_data['cep'][0]
    assert melhor_rota[-1] == coordenadas_data['cep'][0]
    assert isinstance(melhor_fitness, float)
    assert melhor_fitness > 0

def test_evoluir_selecao_cruzamento_mutacao():
    coordenadas_data = {
        'cep': ['82821020', '82821111', '82821222', '82821333'],
        'latitude': [-25.4284, -25.4294, -25.4304, -25.4314],
        'longitude': [-49.2733, -49.2743, -49.2753, -49.2763]
    }
    coordenadas = pd.DataFrame(coordenadas_data)
    vento_previsao = {
        1: {'06:00:00': {'velocidade': 10, 'angulo': 90}, '09:00:00': {'velocidade': 5, 'angulo': 180}},
        2: {'06:00:00': {'velocidade': 15, 'angulo': 270}, '09:00:00': {'velocidade': 20, 'angulo': 0}},
    }
    populacao_tamanho = 5
    geracoes = 2
    velocidade_base = 50
    algoritmo = AlgoritmoGenetico(coordenadas, populacao_tamanho, geracoes, velocidade_base, vento_previsao)

    with patch('random.random', return_value=0.05):
        with patch.object(algoritmo, 'selecionar_pais') as mock_selecionar_pais:
            mock_selecionar_pais.return_value = (algoritmo.populacao[0], algoritmo.populacao[1])
            with patch.object(algoritmo, 'mutacao') as mock_mutacao:
                melhor_rota, melhor_fitness = algoritmo.evoluir()
                assert len(algoritmo.populacao) == populacao_tamanho
                assert mock_selecionar_pais.called, "selecionar_pais should have been called."
                assert mock_mutacao.called, "mutacao should have been called."
                for filho in algoritmo.populacao:
                    assert filho[0] == coordenadas_data['cep'][0]
                    assert filho[-1] == coordenadas_data['cep'][0]

def test_gerar_csv_solucao():
    melhor_rota = ['82821020', '82821111', '82821222']
    nome_arquivo = 'solucao_teste.csv'
    algoritmo.gerar_csv_solucao(melhor_rota, nome_arquivo)

    assert os.path.exists(nome_arquivo)
    with open(nome_arquivo, 'r', encoding='utf-8') as file:
        linhas = file.readlines()
        assert len(linhas) > 1
        cabecalho = linhas[0].strip().split(',')
        campos_esperados = ['CEP inicial', 'Latitude inicial', 'Longitude inicial', 'Dia do voo',
                            'Hora inicial', 'Velocidade', 'CEP final', 'Latitude final', 'Longitude final',
                            'Pouso', 'Hora final']
        assert cabecalho == campos_esperados
        primeira_linha = linhas[1].strip().split(',')
        ultima_linha = linhas[-1].strip().split(',')

        assert primeira_linha[0] == '82821020'
        assert ultima_linha[6] == '82821020'

        for linha in linhas[1:]:
            dia_do_voo = int(linha.split(',')[3])
            assert dia_do_voo <= 5
    os.remove(nome_arquivo)

def test_calcula_fitness_rota_invalida():
    rota_invalida = ['82821111', '82821222', '82821020']
    fitness = algoritmo.calcula_fitness(rota_invalida)
    assert fitness == float('inf')

    rota_invalida = ['82821020', '82821111', '82821222']
    fitness = algoritmo.calcula_fitness(rota_invalida)
    assert fitness == float('inf')

def test_selecionar_pais():
    algoritmo.populacao = [
        ['82821020', '82821111', '82821222', '82821020'],
        ['82821020', '82821333', '82821444', '82821020'],
        ['82821020', '82821222', '82821333', '82821020'],
        ['82821020', '82821444', '82821111', '82821020'],
        ['82821020', '82821111', '82821444', '82821020']
    ]
    pai1, pai2 = algoritmo.selecionar_pais()

    assert pai1 in algoritmo.populacao, "pai1 não está na população"
    assert pai2 in algoritmo.populacao, "pai2 não está na população"
    assert pai1 != pai2, "Os pais selecionados devem ser diferentes"

def test_cruzamento_ajuste_comprimento():
    pai1 = ['82821020', '82821111', '82821222', '82821020']
    pai2 = ['82821020', '82821333', '82821444', '82821555', '82821020']

    filho = algoritmo.cruzamento(pai1, pai2)
    filho[0] = pai1[0]
    filho[-1] = pai1[-1]
    assert len(filho) == len(pai1)
    assert filho[0] == pai1[0]
    assert filho[-1] == pai1[-1]

def test_verifica_arquivo_solucao():
    nome_arquivo = 'solucao_teste.csv'
    conteudo_csv = """CEP inicial,Latitude inicial,Longitude inicial,Dia do voo,Hora inicial,Velocidade,CEP final,Latitude final,Longitude final,Pouso,Hora final
82821020,-25.4284,-49.2733,5,18:30:00,50,82821020,-25.4284,-49.2733,SIM,18:59:00
"""
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo_csv)
    assert verifica_arquivo_solucao(nome_arquivo) == True

    conteudo_csv = """CEP inicial,Latitude inicial,Longitude inicial,Dia do voo,Hora inicial,Velocidade,CEP final,Latitude final,Longitude final,Pouso,Hora final
82821020,-25.4284,-49.2733,5,18:30:00,50,82821020,-25.4284,-49.2733,SIM,19:01:00
"""
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo_csv)
    assert verifica_arquivo_solucao(nome_arquivo) == False
    os.remove(nome_arquivo)
    assert verifica_arquivo_solucao("arquivo_inexistente.csv") == False


def test_calcula_fitness_distancia_excede_limite():
    coordenadas_data = {
        'cep': ['82821020', '99999999'],
        'latitude': [-25.4284, -25.7000],
        'longitude': [-49.2733, -49.5000]
    }
    coordenadas = pd.DataFrame(coordenadas_data)
    vento_previsao = {
        1: {'06:00:00': {'velocidade': 10, 'angulo': 90}, '09:00:00': {'velocidade': 5, 'angulo': 180}},
    }
    algoritmo = AlgoritmoGenetico(coordenadas, populacao_tamanho=2, geracoes=2, velocidade_base=50,
                                  vento_previsao=vento_previsao)

    rota_invalida = ['82821020', '99999999', '82821020']

    fitness = algoritmo.calcula_fitness(rota_invalida)
    assert fitness == float('inf'), "O fitness deveria ser infinito para uma rota inválida."


def test_ajuste_rota_final_unibrasil_dias_incrementados():
    coordenadas_data = {
        'cep': ['82821020', '82821111', '82821222'],
        'latitude': [-25.4284, -25.5284, -25.6284],
        'longitude': [-49.2733, -49.3733, -49.4733]
    }
    coordenadas = pd.DataFrame(coordenadas_data)
    velocidade_base = 50
    algoritmo = AlgoritmoGenetico(
        coordenadas, populacao_tamanho=1, geracoes=1, velocidade_base=velocidade_base, vento_previsao=vento_previsao
    )

    mock_writer = MagicMock()
    csv_writer_mock = MagicMock(return_value=mock_writer)

    with patch("calculo.calcula_distancia", side_effect=lambda lat1, lon1, lat2, lon2: 25000), \
            patch("calculo.calcula_angulo", side_effect=lambda lat1, lon1, lat2, lon2: 90), \
            patch("calculo.ajusta_velocidade", side_effect=lambda base, vento_vel, vento_angulo, voo_angulo: base), \
            patch("builtins.open", new_callable=MagicMock), \
            patch("csv.DictWriter", csv_writer_mock):

        melhor_rota = ['82821222', '82821111', '82821020'] * 100
        melhor_rota.append('82821020')

        dias_validos = sorted(vento_previsao.keys())
        horarios_validos = sorted(list(vento_previsao[1].keys()))
        algoritmo.obtem_previsao_vento = lambda dia, hora: (
            dias_validos[(dia - 1) % len(dias_validos)],
            horarios_validos[hora % len(horarios_validos)]
        )

        algoritmo.gerar_csv_solucao(melhor_rota, nome_arquivo="mock.csv")

        mock_writer.writerow.assert_called()
        chamadas = mock_writer.writerow.call_args_list

        dias_usados = set()
        for idx, chamada in enumerate(chamadas):
            linha = chamada[0][0]
            dias_usados.add(linha['Dia do voo'])
            print(f"Chamada {idx + 1}: Dia do voo = {linha['Dia do voo']}, Hora final = {linha['Hora final']}")

        assert dias_usados == {1, 2, 3, 4, 5}, f"Os dias usados deveriam ser de 1 a 5, mas foram {dias_usados}"

        ultima_chamada = chamadas[-1][0][0]
        assert ultima_chamada[
                   'CEP final'] == '82821020', f"O CEP final deveria ser ajustado para UniBrasil, mas foi {ultima_chamada['CEP final']}."




