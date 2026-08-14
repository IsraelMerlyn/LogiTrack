import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI, status

# Aplicación mínima para la lección de testing y optimización
app = FastAPI(title="LogiTrack Test Target")

def calcular_tarifa_envio(peso_kg: float, distancia_km: float) -> float:
    """Lógica pura de negocio a probar con Pytest"""
    if peso_kg <= 0 or distancia_km <= 0:
        raise ValueError("Peso y distancia deben ser positivos")
    tarifa_base = 50.0
    return tarifa_base + (peso_kg * 2.5) + (distancia_km * 1.2)

@app.get("/api/v1/cotizar")
def endpoint_cotizar(peso: float, distancia: float):
    try:
        total = calcular_tarifa_envio(peso, distancia)
        return {"peso": peso, "distancia": distancia, "tarifa_total": total}
    except ValueError as e:
        return {"error": str(e)}, 400

client = TestClient(app)

# === PRUEBAS UNITARIAS ===
def test_calcular_tarifa_envio_exitoso():
    # 10kg, 100km -> 50 + (10 * 2.5) + (100 * 1.2) = 50 + 25 + 120 = 195.0
    resultado = calcular_tarifa_envio(10.0, 100.0)
    assert resultado == 195.0

def test_calcular_tarifa_envio_valores_invalidos():
    with pytest.raises(ValueError):
        calcular_tarifa_envio(-5.0, 100.0)

def test_mocking_servicio_externo(mocker):
    # Simular una API externa de geolocalización / mapas con Pytest-Mock
    mock_geo_api = mocker.patch("spike_7_7.test_suite.calcular_tarifa_envio", return_value=300.0)
    
    tarifa = mock_geo_api(10, 50)
    assert tarifa == 300.0
    mock_geo_api.assert_called_once_with(10, 50)

# === PRUEBAS DE INTEGRACIÓN (HTTP) ===
def test_endpoint_cotizar_200():
    response = client.get("/api/v1/cotizar?peso=10&distancia=100")
    assert response.status_code == 200
    assert response.json()["tarifa_total"] == 195.0

def test_endpoint_cotizar_400():
    response = client.get("/api/v1/cotizar?peso=-10&distancia=100")
    assert response.status_code == 200 # Manejado por el controlador
    assert "error" in response.json()
