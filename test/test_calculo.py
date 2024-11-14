import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from calculo import calcula_distancia, ajusta_velocidade, calcula_angulo



def test_calcula_distancia():
    lat1, lon1 = -25.4284, -49.2733
    lat2, lon2 = -25.4294, -49.2723

    distancia = calcula_distancia(lat1, lon1, lat2, lon2)
    assert isinstance(distancia, float)
    assert distancia > 0
    assert abs(distancia - 149.8) < 1

def test_ajusta_velocidade():
    velocidade_base = 50
    vento_velocidade = 10
    vento_angulo = 90
    angulo_voo = 0

    velocidade_ajustada = ajusta_velocidade(velocidade_base, vento_velocidade, vento_angulo, angulo_voo)
    assert isinstance(velocidade_ajustada, int)
    assert 30 <= velocidade_ajustada <= 60
    assert ajusta_velocidade(50, 10, 0, 0) == 60
    assert ajusta_velocidade(50, 10, 180, 0) == 40



def test_calcula_angulo():

    lat1, lon1 = -25.4284, -49.2733
    lat2, lon2 = -25.4294, -49.2723

    angulo = calcula_angulo(lat1, lon1, lat2, lon2)
    assert isinstance(angulo, float)
    assert 0 <= angulo < 360
    assert abs(angulo - 137.9) < 1

