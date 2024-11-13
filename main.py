import pandas as pd
from previsao import vento_previsao
from algoritimo import AlgoritmoGenetico, verifica_arquivo_solucao

# Leitura das coordenadas a partir de um arquivo CSV
coordenadas_df = pd.read_csv('coordenadas.csv')

print("Buscando melhor rota...")  # Mensagem inicial

while True:
    # Instanciar o algoritmo genético
    ag = AlgoritmoGenetico(
        coordenadas=coordenadas_df,
        populacao_tamanho=10,
        geracoes=2,
        velocidade_base=30,
        vento_previsao=vento_previsao
    )

    # Evoluir para encontrar a melhor rota
    melhor_rota, _ = ag.evoluir()

    # Geração do arquivo CSV com a melhor rota
    ag.gerar_csv_solucao(melhor_rota, nome_arquivo='solucao.csv')

    # Verifica se o horário final está dentro do limite
    if verifica_arquivo_solucao('solucao.csv'):
        print("Solução encontrada!")
        break
