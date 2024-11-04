from calculo import calcula_angulo,calcula_distancia,ajusta_velocidade
import math
import random
import csv


class AlgoritmoGenetico:
    def __init__(self, coordenadas, populacao_tamanho, geracoes, velocidade_base, vento_previsao):
        self.coordenadas = coordenadas
        self.populacao_tamanho = populacao_tamanho
        self.geracoes = geracoes
        self.velocidade_base = velocidade_base
        self.vento_previsao = vento_previsao
        self.populacao = self.gera_populacao_inicial()

    def gera_populacao_inicial(self):
        ceps = self.coordenadas['cep'].tolist()
        cep_unibrasil = ceps[0]  # Supondo que o primeiro CEP seja o da UniBrasil
        ceps = ceps[1:]  # Remove a UniBrasil da lista para evitar duplicação

        populacao = []
        for _ in range(self.populacao_tamanho):
            rota = [cep_unibrasil] + random.sample(ceps, len(ceps)) + [cep_unibrasil]
            populacao.append(rota)

        return populacao

    def calcula_fitness(self, rota):
        custo_total = 0
        tempo_total = 0
        bateria_restante = 1800
        hora_atual = 21600  # 06:00:00 em segundos
        dia_atual = 1

        cep_unibrasil = self.coordenadas['cep'].iloc[0]
        if rota[0] != cep_unibrasil or rota[-1] != cep_unibrasil:
            return float('inf')  # Penalizar se a rota não começa/termina na UniBrasil

        for i in range(1, len(rota)):
            cep_inicial = rota[i - 1]
            cep_final = rota[i]
            coord_inicial = self.coordenadas[self.coordenadas['cep'] == cep_inicial]
            coord_final = self.coordenadas[self.coordenadas['cep'] == cep_final]
            lat1, lon1 = coord_inicial['latitude'].values[0], coord_inicial['longitude'].values[0]
            lat2, lon2 = coord_final['latitude'].values[0], coord_final['longitude'].values[0]

            distancia = calcula_distancia(lat1, lon1, lat2, lon2)
            angulo_voo = calcula_angulo(lat1, lon1, lat2, lon2)
            dia_voo, horario_voo = self.obtem_previsao_vento(dia_atual, hora_atual)
            velocidade_ajustada = ajusta_velocidade(
                self.velocidade_base,
                self.vento_previsao[dia_voo][horario_voo]['velocidade'],
                self.vento_previsao[dia_voo][horario_voo]['angulo'],
                angulo_voo
            )

            tempo_voo = distancia / (velocidade_ajustada * 1000 / 3600)
            tempo_total += math.ceil(tempo_voo)
            bateria_restante -= math.ceil(tempo_voo)
            hora_atual += math.ceil(tempo_voo)

            # Verificar se é necessário recarregar e ajustar o tempo
            if bateria_restante <= 0 or hora_atual >= 68400:  # 19:00:00 em segundos
                custo_total += 60  # Custo de recarga
                bateria_restante = 1800
                if hora_atual >= 68400:  # Se for após as 19:00, recarregar até o próximo dia
                    dia_atual += 1
                    hora_atual = 21600  # Voltar para 06:00:00
                else:
                    hora_atual += 60  # Tempo de recarga durante o dia

            tempo_total += 60
            bateria_restante -= 60
            hora_atual += 60  # Considerar o tempo de tirar fotos

            if dia_atual > 5:  # Não pode ultrapassar os 5 dias
                return float('inf')  # Penalizar rotas que excedam os 5 dias

        return 1 / (tempo_total + custo_total)

    def obtem_previsao_vento(self, dia, hora):
        # Arredonda o horário para o múltiplo de 3 horas mais próximo: 06:00, 09:00, 12:00, etc.
        horas_disponiveis = [6, 9, 12, 15, 18]  # Horários padrão da previsão
        hora_atual = hora // 3600  # Converter de segundos para horas
        hora_arredondada = min(horas_disponiveis, key=lambda x: abs(x - hora_atual))
        hora_formatada = f"{hora_arredondada:02}:00:00"
        return dia, hora_formatada

    def selecionar_pais(self):
        pais = random.sample(self.populacao, 2)
        return pais[0], pais[1]

    def cruzamento(self, pai1, pai2):
        ponto_corte = random.randint(1, len(pai1) - 1)
        filho = pai1[:ponto_corte] + [cidade for cidade in pai2 if cidade not in pai1[:ponto_corte]]
        return filho

    def mutacao(self, individuo):
        i, j = random.sample(range(len(individuo)), 2)
        individuo[i], individuo[j] = individuo[j], individuo[i]

    def evoluir(self):
        for geracao in range(self.geracoes):
            print(f"Geracao: {geracao + 1}/{self.geracoes}")  # Depuração: indica o progresso
            fitnesses = [(self.calcula_fitness(rota), rota) for rota in self.populacao]
            fitnesses.sort(reverse=True, key=lambda x: x[0])
            nova_populacao = [rota for _, rota in fitnesses[:2]]

            while len(nova_populacao) < self.populacao_tamanho:
                pai1, pai2 = self.selecionar_pais()
                filho = self.cruzamento(pai1, pai2)
                if random.random() < 0.1:
                    self.mutacao(filho)
                nova_populacao.append(filho)

            self.populacao = nova_populacao

        melhor_fitness, melhor_rota = fitnesses[0]
        return melhor_rota, 1 / melhor_fitness

    def gerar_csv_solucao(self, melhor_rota, nome_arquivo='solucao1.csv'):
        with open(nome_arquivo, 'w', newline='') as csvfile:
            fieldnames = ['CEP inicial', 'Latitude inicial', 'Longitude inicial', 'Dia do voo',
                          'Hora inicial', 'Velocidade', 'CEP final', 'Latitude final', 'Longitude final',
                          'Pouso', 'Hora final']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            hora_atual = 21600  # 06:00:00 em segundos
            dia_atual = 1
            bateria_restante = 1800  # Autonomia inicial em segundos (30 minutos)

            for i in range(1, len(melhor_rota)):
                if dia_atual > 5:  # Limite de dias atingido
                    print("Atingido o limite de 5 dias. Encerrando a geração do CSV.")
                    break

                cep_inicial = melhor_rota[i - 1]
                cep_final = melhor_rota[i]
                coord_inicial = self.coordenadas[self.coordenadas['cep'] == cep_inicial]
                coord_final = self.coordenadas[self.coordenadas['cep'] == cep_final]
                lat1, lon1 = coord_inicial['latitude'].values[0], coord_inicial['longitude'].values[0]
                lat2, lon2 = coord_final['latitude'].values[0], coord_final['longitude'].values[0]

                # Calcular a distância e o ângulo de voo
                distancia = calcula_distancia(lat1, lon1, lat2, lon2)
                angulo_voo = calcula_angulo(lat1, lon1, lat2, lon2)

                # Obter a previsão de vento para ajustar a velocidade
                dia_voo, horario_voo = self.obtem_previsao_vento(dia_atual, hora_atual)
                if dia_voo in self.vento_previsao and horario_voo in self.vento_previsao[dia_voo]:
                    velocidade_ajustada = ajusta_velocidade(
                        self.velocidade_base,
                        self.vento_previsao[dia_voo][horario_voo]['velocidade'],
                        self.vento_previsao[dia_voo][horario_voo]['angulo'],
                        angulo_voo
                    )
                else:
                    # Usar valores padrão se o dia ou horário não existir na previsão de vento
                    print(f"Usando valores padrão para dia {dia_voo}, horário {horario_voo}")
                    velocidade_ajustada = self.velocidade_base

                # Calcular o tempo de voo e ajustar a hora
                tempo_voo = distancia / (velocidade_ajustada * 1000 / 3600)
                tempo_voo = math.ceil(tempo_voo)
                hora_formatada_inicio = f"{hora_atual // 3600:02}:{(hora_atual % 3600) // 60:02}:00"
                hora_atual += tempo_voo
                hora_formatada_fim = f"{hora_atual // 3600:02}:{(hora_atual % 3600) // 60:02}:00"

                # Ajustar o consumo de bateria
                bateria_restante -= tempo_voo

                # Verificar se precisa recarregar
                pouso = 'NÃO'
                if bateria_restante <= 0 or hora_atual >= 68400:  # 19:00:00 em segundos
                    pouso = 'SIM'
                    bateria_restante = 1800  # Recarregar a bateria
                    if hora_atual >= 68400:  # Se for após 19:00, avançar para o próximo dia
                        dia_atual += 1
                        hora_atual = 21600  # Reiniciar para 06:00:00 do dia seguinte
                    else:
                        hora_atual += 60  # Adicionar 60 segundos para recarga durante o dia
                    hora_formatada_fim = f"{hora_atual // 3600:02}:{(hora_atual % 3600) // 60:02}:00"

                # Adicionar o tempo de tirar fotos (60 segundos)
                hora_atual += 60
                bateria_restante -= 60

                # Gravar os dados do trecho no arquivo CSV
                writer.writerow({
                    'CEP inicial': cep_inicial,
                    'Latitude inicial': lat1,
                    'Longitude inicial': lon1,
                    'Dia do voo': dia_atual,
                    'Hora inicial': hora_formatada_inicio,
                    'Velocidade': velocidade_ajustada,
                    'CEP final': cep_final,
                    'Latitude final': lat2,
                    'Longitude final': lon2,
                    'Pouso': pouso,
                    'Hora final': hora_formatada_fim
                })

        print(f"Arquivo CSV '{nome_arquivo}' gerado com sucesso.")
