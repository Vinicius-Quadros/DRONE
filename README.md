
# UNIBRASIL Maps

Este projeto é parte de uma atividade supervisionada na UniBrasil para criar um sistema de mapeamento autônomo usando um drone com GPS para fotografar áreas específicas na cidade de Curitiba. O sistema calcula a rota ideal para que o drone visite todas as coordenadas, retornando ao ponto de origem, e minimizando o custo de operação, medido pelo tempo total de voo e pela quantidade de paradas para recarga.

## Objetivo

O objetivo do **UNIBRASIL Maps** é:
- **Fotografar pontos específicos** (definidos por CEPs) em Curitiba, conforme coordenadas fornecidas.
- **Minimizar o custo de voo** através da redução de tempo e paradas.
- **Retornar ao ponto inicial** no Campus UniBrasil ao final do trajeto.
  
## Tecnologias e Algoritmo

O projeto utiliza um **algoritmo genético**, uma técnica de computação evolucionária, para otimizar a rota do drone. Esse algoritmo encontra a sequência de pontos e horários ideais para o drone realizar as capturas sem ultrapassar o limite de bateria e dentro dos horários permitidos de voo (06:00 às 19:00).

### Principais Tecnologias e Bibliotecas
- **Linguagem**: Python
- **Versão necessária**: Python 3.10 ou superior
- **Bibliotecas utilizadas**:
  - `calculo` (módulo customizado) para cálculos de ângulo, distância e ajuste de velocidade.
  - `math` para operações matemáticas essenciais.
  - `random` para gerar valores aleatórios no algoritmo genético.
  - `csv` para manipulação de arquivos CSV.
  - `datetime` para controle de datas e horários de voo.
  - `pandas` para análise e manipulação de dados.
  - `sys` e `os` para manipulação de caminhos de arquivos e configurações de ambiente.
  - `pytest` para execução dos testes unitários.
  - `unittest.mock` para criação de mocks nos testes.

## Estrutura do Projeto

O projeto é dividido nas seguintes pastas e arquivos:

```
DRONE/
├── main.py                # Script principal para execução do algoritmo
├── algoritimo.py          # Implementação do algoritmo genético
├── calculo.py             # Funções de cálculo de distância e ajuste de velocidade
├── previsao.py            # Previsão de vento e condições climáticas
├── coordenadas.csv        # Arquivo com as coordenadas de CEPs
└── tests/                 # Pasta com os testes unitários
    ├── test_algoritimo.py # Testes para o algoritmo genético
    ├── test_calculo.py    # Testes para as funções de cálculo
```

## Como Executar o Projeto

1. **Instale as dependências**:
   Para garantir o correto funcionamento do projeto, instale as bibliotecas abaixo utilizando o `pip`:

   ```bash
   pip install numpy
   pip install pandas
   pip install geopy
   pip install matplotlib
   pip install pytest
   pip install coverage
   ```

2. **Execute o projeto**:
   O projeto é executado pelo arquivo `main.py`, que processa os dados e gera uma saída `solucao.csv` com a rota otimizada do drone. Execute com o comando:
   ```bash
   python main.py
   ```

3. **Testes**:
   Para garantir a funcionalidade do código e obter a cobertura de testes, execute o comando:
   ```bash
   python -m coverage run -m pytest
   ```

## Arquivo de Saída

A execução gera um arquivo `solucao.csv`, que contém:
- CEP inicial e final de cada trecho.
- Latitude e longitude de cada ponto.
- Dia e hora de início e término do voo para cada ponto.
- Indicação de pouso para recarga ou parada para foto.

## Considerações Finais

Este projeto foi desenvolvido como parte do curso na UniBrasil e visa aplicar conhecimentos em algoritmos evolucionários, otimização de rotas, e integração de dados geográficos com previsões meteorológicas para o planejamento autônomo de drones.
