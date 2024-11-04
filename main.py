import pandas as pd
from previsao import vento_previsao
from algoritimo import AlgoritmoGenetico

# Leitura das coordenadas a partir de um arquivo CSV
coordenadas_df = pd.read_csv('coordenadas.csv')

# Instanciar o algoritmo genético
ag = AlgoritmoGenetico(
    coordenadas=coordenadas_df,
    populacao_tamanho=10,  # População pequena para teste
    geracoes=10,  # Menor número de gerações para verificar execução
    velocidade_base=30,
    vento_previsao=vento_previsao
)

# Evoluir para encontrar a melhor rota
melhor_rota, melhor_tempo = ag.evoluir()

# Geração do arquivo CSV com a melhor rota
ag.gerar_csv_solucao(melhor_rota, nome_arquivo='solucao.csv')

print(f"Melhor rota encontrada: {melhor_rota}")
print(f"Tempo total (s): {melhor_tempo}")
