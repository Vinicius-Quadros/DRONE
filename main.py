import pandas as pd
from previsao import vento_previsao
from algoritimo import AlgoritmoGenetico, verifica_arquivo_solucao

coordenadas_df = pd.read_csv('coordenadas.csv')

print("Buscando melhor rota...")

while True:
    ag = AlgoritmoGenetico(
        coordenadas=coordenadas_df,
        populacao_tamanho=10,
        geracoes=2,
        velocidade_base=30,
        vento_previsao=vento_previsao
    )
    melhor_rota, _ = ag.evoluir()
    ag.gerar_csv_solucao(melhor_rota, nome_arquivo='solucao.csv')
    if verifica_arquivo_solucao('solucao.csv'):
        print("Solução encontrada!")
        break