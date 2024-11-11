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

    @staticmethod
    def obtem_previsao_vento(dia, hora):
        # Arredonda o horário para o múltiplo de 3 horas mais próximo: 06:00, 09:00, 12:00, etc.
        horas_disponiveis = [6, 9, 12, 15, 18]  # Horários padrão da previsão
        hora_atual = hora // 3600  # Converter de segundos para horas
        hora_arredondada = min(horas_disponiveis, key=lambda x: abs(x - hora_atual))
        hora_formatada = f"{hora_arredondada:02}:00:00"
        return dia, hora_formatada

    def selecionar_pais(self):
        pais = random.sample(self.populacao, 2)
        return pais[0], pais[1]

    @staticmethod
    def cruzamento(pai1, pai2):
        ponto_corte = random.randint(1, len(pai1) - 2)  # Define ponto de corte sem alterar início/fim
        filho = pai1[:ponto_corte]  # Primeira parte do filho vem do pai1 até o ponto de corte

        # Adiciona as cidades do pai2 que ainda não estão no filho, mantendo a ordem
        for cidade in pai2:
            if cidade not in filho:
                filho.append(cidade)

        # Garante que o início e o fim do filho sejam os mesmos do pai1
        filho[0] = pai1[0]
        filho[-1] = pai1[-1]

        # Ajusta o tamanho do filho se necessário
        if len(filho) > len(pai1):
            filho = filho[:len(pai1)]
        elif len(filho) < len(pai1):
            # Adiciona pontos que possam estar faltando para garantir o tamanho correto
            for cidade in pai1:
                if cidade not in filho:
                    filho.insert(-1, cidade)  # Insere antes do último ponto

        return filho

    @staticmethod
    def mutacao(individuo):
        i, j = random.sample(range(1, len(individuo) - 1), 2)  # Evita alterar o primeiro e último pontos
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
                # Garante que a última posição do filho seja sempre a UniBrasil
                filho[-1] = self.coordenadas['cep'].iloc[0]
                nova_populacao.append(filho)

            self.populacao = nova_populacao

        melhor_fitness, melhor_rota = fitnesses[0]
        cep_unibrasil = self.coordenadas['cep'].iloc[0]  # Assumindo que o primeiro CEP é o da UniBrasil

        # Força o último ponto da rota para ser o CEP da UniBrasil
        if melhor_rota[-1] != cep_unibrasil:
            melhor_rota = melhor_rota[:-1] + [cep_unibrasil]

        return melhor_rota, 1 / melhor_fitness

    def gerar_csv_solucao(self, melhor_rota, nome_arquivo='solucao.csv'):
        cep_unibrasil = self.coordenadas['cep'].iloc[0]  # CEP da UniBrasil
        if melhor_rota[-1] != cep_unibrasil:
            melhor_rota[-1] = cep_unibrasil  # Força o retorno ao final

        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['CEP inicial', 'Latitude inicial', 'Longitude inicial', 'Dia do voo',
                          'Hora inicial', 'Velocidade', 'CEP final', 'Latitude final', 'Longitude final',
                          'Pouso', 'Hora final']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            hora_atual = 21600  # 06:00:00 em segundos
            dia_atual = 1
            bateria_restante = 1800  # Autonomia inicial em segundos (30 minutos)
            cep_inicial = melhor_rota[0]  # Iniciar sempre na UniBrasil

            for i in range(1, len(melhor_rota)):
                if dia_atual > 5:
                    break

                cep_final = melhor_rota[i]
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
                tempo_voo = math.ceil(tempo_voo)
                hora_formatada_inicio = f"{hora_atual // 3600:02}:{(hora_atual % 3600) // 60:02}:00"

                # Verifica se o tempo de voo atual ultrapassa 19:00
                if hora_atual + tempo_voo > 68400:
                    # Se for o último dia, força o retorno à UniBrasil
                    if dia_atual == 5 and cep_final != cep_unibrasil:
                        coord_final = self.coordenadas[self.coordenadas['cep'] == cep_unibrasil]
                        lat2, lon2 = coord_final['latitude'].values[0], coord_final['longitude'].values[0]
                        distancia = calcula_distancia(lat1, lon1, lat2, lon2)  # Recalcula a distância
                        tempo_voo = distancia / (self.velocidade_base * 1000 / 3600)
                        tempo_voo = math.ceil(tempo_voo)  # Recalcula o tempo de voo com a velocidade base

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
                    hora_atual = 21600  # Reinicia no próximo dia às 06:00:00
                    dia_atual += 1
                    bateria_restante = 1800
                    if dia_atual > 5:
                        break
                    continue

                # Atualiza o estado após o voo
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

                # Atualiza a bateria e o próximo ponto inicial
                bateria_restante -= tempo_voo
                if pouso_necessario:
                    bateria_restante = 1800
                cep_inicial = cep_final

                # Adiciona 1 minuto ao horário para o início da próxima linha
                hora_atual += 60