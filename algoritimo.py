from calculo import calcula_angulo,calcula_distancia,ajusta_velocidade
import math
import random
import csv
from datetime import datetime

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
        cep_unibrasil = ceps[0]
        ceps = ceps[1:]

        populacao = []
        for _ in range(self.populacao_tamanho):
            rota = [cep_unibrasil] + random.sample(ceps, len(ceps)) + [cep_unibrasil]
            populacao.append(rota)

        return populacao

    @staticmethod
    def obtem_previsao_vento(dia, hora):
        horas_disponiveis = [6, 9, 12, 15, 18]
        hora_atual = hora // 3600
        hora_arredondada = min(horas_disponiveis, key=lambda x: abs(x - hora_atual))
        hora_formatada = f"{hora_arredondada:02}:00:00"
        return dia, hora_formatada

    def selecionar_pais(self):
        pais = random.sample(self.populacao, 2)
        return pais[0], pais[1]

    @staticmethod
    def cruzamento(pai1, pai2):
        ponto_corte = random.randint(1, len(pai1) - 2)
        filho = pai1[:ponto_corte]
        for cidade in pai2:
            if cidade not in filho:
                filho.append(cidade)

        filho[0] = pai1[0]
        filho[-1] = pai1[-1]

        if len(filho) > len(pai1):
            filho = filho[:len(pai1)]
        elif len(filho) < len(pai1):
            for cidade in pai1:
                if cidade not in filho:
                    filho.insert(-1, cidade)

        return filho

    @staticmethod
    def mutacao(individuo):
        i, j = random.sample(range(1, len(individuo) - 1), 2)
        individuo[i], individuo[j] = individuo[j], individuo[i]

    def calcula_fitness(self, rota):
        custo_total = 0
        tempo_total = 0
        bateria_restante = 1800
        hora_atual = 21600  # 06:00:00 em segundos
        dia_atual = 1

        cep_unibrasil = self.coordenadas['cep'].iloc[0]
        if rota[0] != cep_unibrasil or rota[-1] != cep_unibrasil:
            return float('inf')

        for i in range(1, len(rota)):
            cep_inicial = rota[i - 1]
            cep_final = rota[i]
            coord_inicial = self.coordenadas[self.coordenadas['cep'] == cep_inicial]
            coord_final = self.coordenadas[self.coordenadas['cep'] == cep_final]
            lat1, lon1 = coord_inicial['latitude'].values[0], coord_inicial['longitude'].values[0]
            lat2, lon2 = coord_final['latitude'].values[0], coord_final['longitude'].values[0]

            distancia = calcula_distancia(lat1, lon1, lat2, lon2)
            if distancia > 15000:  # 15 km
                return float('inf')  # Rota inválida

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
            taxa_de_consumo = (velocidade_ajustada / self.velocidade_base) ** 3
            bateria_restante -= math.ceil(tempo_voo * taxa_de_consumo)
            hora_atual += math.ceil(tempo_voo)

            if bateria_restante <= 0 or hora_atual >= 68400:  # 19:00:00 em segundos
                custo_total += 60
                bateria_restante = 1800
                if hora_atual >= 68400:
                    dia_atual += 1
                    hora_atual = 21600
                else:
                    hora_atual += 60

            tempo_total += 60
            bateria_restante -= 60
            hora_atual += 60

            if dia_atual > 5:
                return float('inf')

        return 1 / (tempo_total + custo_total)

    def evoluir(self):
        for _ in range(self.geracoes):
            fitnesses = [(self.calcula_fitness(rota), rota) for rota in self.populacao]
            fitnesses.sort(reverse=True, key=lambda x: x[0])
            nova_populacao = [rota for _, rota in fitnesses[:2]]

            while len(nova_populacao) < self.populacao_tamanho:
                pai1, pai2 = self.selecionar_pais()
                filho = self.cruzamento(pai1, pai2)
                if random.random() < 0.1:
                    self.mutacao(filho)
                filho[-1] = self.coordenadas['cep'].iloc[0]
                nova_populacao.append(filho)

            self.populacao = nova_populacao

        melhor_fitness, melhor_rota = fitnesses[0]
        cep_unibrasil = self.coordenadas['cep'].iloc[0]

        if melhor_rota[-1] != cep_unibrasil:
            melhor_rota = melhor_rota[:-1] + [cep_unibrasil]

        return melhor_rota, 1 / melhor_fitness

    def gerar_csv_solucao(self, melhor_rota, nome_arquivo='solucao.csv'):
        cep_unibrasil = self.coordenadas['cep'].iloc[0]
        if melhor_rota[-1] != cep_unibrasil:
            melhor_rota[-1] = cep_unibrasil

        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['CEP inicial', 'Latitude inicial', 'Longitude inicial', 'Dia do voo',
                          'Hora inicial', 'Velocidade', 'CEP final', 'Latitude final', 'Longitude final',
                          'Pouso', 'Hora final']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            hora_atual = 21600
            dia_atual = 1
            bateria_restante = 1800
            cep_inicial = melhor_rota[0]

            for i in range(1, len(melhor_rota)):
                if dia_atual > 5:
                    break

                cep_final = melhor_rota[i]
                coord_inicial = self.coordenadas[self.coordenadas['cep'] == cep_inicial]
                coord_final = self.coordenadas[self.coordenadas['cep'] == cep_final]
                lat1, lon1 = coord_inicial['latitude'].values[0], coord_inicial['longitude'].values[0]
                lat2, lon2 = coord_final['latitude'].values[0], coord_final['longitude'].values[0]

                distancia = calcula_distancia(lat1, lon1, lat2, lon2)
                if distancia > 15000:  # 15 km
                    continue  # Pule para o próximo destino

                angulo_voo = calcula_angulo(lat1, lon1, lat2, lon2)
                dia_voo, horario_voo = self.obtem_previsao_vento(dia_atual, hora_atual)
                velocidade_ajustada = ajusta_velocidade(
                    self.velocidade_base,
                    self.vento_previsao[dia_voo][horario_voo]['velocidade'],
                    self.vento_previsao[dia_voo][horario_voo]['angulo'],
                    angulo_voo
                )

                tempo_voo = distancia / (velocidade_ajustada * 1000 / 3600)
                tempo_voo = math.ceil(tempo_voo)
                hora_formatada_inicio = f"{hora_atual // 3600:02}:{(hora_atual % 3600) // 60:02}:00"

                if hora_atual + tempo_voo > 68400:  # Após 19:00:00
                    if dia_atual == 5 and cep_final != cep_unibrasil:
                        coord_final = self.coordenadas[self.coordenadas['cep'] == cep_unibrasil]
                        lat2, lon2 = coord_final['latitude'].values[0], coord_final['longitude'].values[0]
                        distancia = calcula_distancia(lat1, lon1, lat2, lon2)
                        tempo_voo = distancia / (self.velocidade_base * 1000 / 3600)
                        tempo_voo = math.ceil(tempo_voo)

                        hora_final = hora_atual + tempo_voo
                        hora_formatada_fim = f"{hora_final // 3600:02}:{(hora_final % 3600) // 60:02}:00"

                        writer.writerow({
                            'CEP inicial': cep_inicial,
                            'Latitude inicial': lat1,
                            'Longitude inicial': lon1,
                            'Dia do voo': dia_atual,
                            'Hora inicial': hora_formatada_inicio,
                            'Velocidade': self.velocidade_base,  # Usa a velocidade base para o último voo
                            'CEP final': cep_unibrasil,
                            'Latitude final': lat2,
                            'Longitude final': lon2,
                            'Pouso': 'SIM',
                            'Hora final': hora_formatada_fim
                        })
                    cep_inicial = cep_inicial
                    hora_atual = 21600
                    dia_atual += 1
                    bateria_restante = 1800
                    if dia_atual > 5:
                        break
                    continue

                hora_atual += tempo_voo
                hora_formatada_fim = f"{hora_atual // 3600:02}:{(hora_atual % 3600) // 60:02}:00"
                pouso_necessario = bateria_restante <= tempo_voo or hora_atual >= 68400
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
                    'Pouso': 'SIM' if pouso_necessario else 'NÃO',
                    'Hora final': hora_formatada_fim
                })

                bateria_restante -= tempo_voo
                if pouso_necessario:
                    bateria_restante = 1800
                cep_inicial = cep_final
                hora_atual += 60

def verifica_arquivo_solucao(nome_arquivo='solucao.csv'):
    try:
        with open(nome_arquivo, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            ultima_linha = None
            for row in reader:
                ultima_linha = row

        if ultima_linha:
            horario_final_str = ultima_linha['Hora final']
            horario_final = datetime.strptime(horario_final_str, "%H:%M:%S").time()
            limite = datetime.strptime("19:00:00", "%H:%M:%S").time()
            return horario_final <= limite
        return False
    except FileNotFoundError:
        return False