import math


# Função para calcular a distância entre duas coordenadas usando a fórmula de Haversine
def calcula_distancia(lat1, lon1, lat2, lon2):
    R = 6371.0  # Raio da Terra em km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distancia = R * c
    return distancia * 1000  # Retorna a distância em metros


# Função para ajustar a velocidade do drone considerando a influência do vento
def ajusta_velocidade(velocidade_base, vento_velocidade, vento_angulo, angulo_voo):
    ajuste = math.cos(math.radians(vento_angulo - angulo_voo)) * vento_velocidade
    velocidade_ajustada = velocidade_base + ajuste
    return max(30, min(60, velocidade_ajustada))


# Função para calcular o ângulo de voo entre dois pontos
def calcula_angulo(lat1, lon1, lat2, lon2):
    dlon = lon2 - lon1
    x = math.cos(math.radians(lat2)) * math.sin(math.radians(dlon))
    y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - \
        math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(dlon))
    angulo = math.degrees(math.atan2(x, y))
    return (angulo + 360) % 360  # Normalizar para um valor entre 0 e 360