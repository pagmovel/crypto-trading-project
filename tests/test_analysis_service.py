import pytest
from datetime import datetime, timedelta
from src.services.analysis_service import AnalysisService
from src.models.market_model import OptionContract

def test_calculate_implied_volatility():
    service = AnalysisService()
    
    # Teste com valores típicos de mercado
    strike = 30000.0  # Preço de exercício
    spot = 29000.0    # Preço atual
    time_to_expiry = 30/365  # 30 dias
    is_call = True
    
    implied_vol = service.calculate_implied_volatility(strike, spot, time_to_expiry, is_call)
    assert 0 < implied_vol < 2.0  # Volatilidade deve estar em um range razoável

def test_calculate_greeks():
    service = AnalysisService()
    
    # Valores de teste
    spot = 29000.0
    strike = 30000.0
    time_to_expiry = 30/365
    volatility = 0.5
    is_call = True
    
    greeks = service.calculate_greeks(spot, strike, time_to_expiry, volatility, is_call)
    
    # Verificações básicas dos Greeks
    assert -1.0 <= greeks.delta <= 1.0  # Delta deve estar entre -1 e 1
    assert greeks.gamma >= 0  # Gamma deve ser positivo
    assert isinstance(greeks.theta, float)  # Theta deve ser um número
    assert greeks.vega >= 0  # Vega deve ser positivo