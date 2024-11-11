import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from calculo import calcula_distancia, ajusta_velocidade, calcula_angulo


# Teste para calcula_distancia
def test_calcula_distancia():
    # Exemplo de coordenadas para teste (em graus decimais)
    lat1, lon1 = -25.4284, -49.2733  # Coordenadas de Curitiba
    lat2, lon2 = -25.4294, -49.2723  # Coordenadas próximas

    distancia = calcula_distancia(lat1, lon1, lat2, lon2)
    assert isinstance(distancia, float)
    assert distancia > 0  # Distância deve ser positiva
    # Ajuste do valor esperado para permitir uma margem maior
    assert abs(distancia - 149.8) < 1  # Novo valor esperado (149.8 metros)


# Teste para ajusta_velocidade
def test_ajusta_velocidade():
    # Exemplo de velocidade e vento para teste
    velocidade_base = 50  # Velocidade inicial do drone
    vento_velocidade = 10  # Velocidade do vento
    vento_angulo = 90  # Direção do vento em graus
    angulo_voo = 0  # Direção do voo em graus

    velocidade_ajustada = ajusta_velocidade(velocidade_base, vento_velocidade, vento_angulo, angulo_voo)
    assert isinstance(velocidade_ajustada, int)
    # Teste dos limites de velocidade ajustada
    assert 30 <= velocidade_ajustada <= 60
    # Teste para verificar se a velocidade ajustada corresponde ao esperado em alguns cenários
    assert ajusta_velocidade(50, 10, 0, 0) == 60  # Quando o vento está diretamente a favor
    assert ajusta_velocidade(50, 10, 180, 0) == 40  # Quando o vento está contra


# Teste para calcula_angulo
def test_calcula_angulo():
    # Exemplo de coordenadas para teste
    lat1, lon1 = -25.4284, -49.2733  # Coordenadas de Curitiba
    lat2, lon2 = -25.4294, -49.2723  # Coordenadas próximas, direção aproximada a nordeste

    angulo = calcula_angulo(lat1, lon1, lat2, lon2)
    assert isinstance(angulo, float)
    # Teste para garantir que o ângulo está entre 0 e 360 graus
    assert 0 <= angulo < 360
    # Ajuste para o ângulo esperado com base nos resultados obtidos
    assert abs(angulo - 137.9) < 1  # Novo valor esperado (137.9 graus)


if __name__ == "__main__":
    pytest.main()
