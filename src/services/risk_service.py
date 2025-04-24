from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
from dataclasses import dataclass

from models.market_model import OptionContract

@dataclass
class PortfolioRisk:
    value_at_risk: float
    expected_shortfall: float
    option_greeks: Dict[str, float]
    stress_test_results: Dict[str, float]
    correlation_matrix: Optional[np.ndarray] = None

class RiskService:
    def __init__(self) -> None:
        self.confidence_level: float = 0.95
        self.lookback_period: int = 252  # Dias úteis em um ano
        
    def calculate_portfolio_risk(self, positions: List[OptionContract], 
                               historical_prices: List[float]) -> PortfolioRisk:
        """
        Calcula métricas de risco para um portfolio de opções
        """
        # Calcula retornos históricos
        returns = np.diff(historical_prices) / historical_prices[:-1]
        
        # Calcula VaR e Expected Shortfall
        var = self._calculate_var(returns)
        es = self._calculate_expected_shortfall(returns)
        
        # Calcula Greeks agregados do portfolio
        greeks = self._aggregate_greeks(positions)
        
        # Executa testes de stress
        stress_results = self._run_stress_tests(positions)
        
        # Calcula matriz de correlação se houver mais de uma posição
        correlation = self._calculate_correlation(positions) if len(positions) > 1 else None
        
        return PortfolioRisk(
            value_at_risk=var,
            expected_shortfall=es,
            option_greeks=greeks,
            stress_test_results=stress_results,
            correlation_matrix=correlation
        )
        
    def _calculate_var(self, returns: np.ndarray) -> float:
        """
        Calcula Value at Risk usando método histórico
        """
        if len(returns) == 0:
            return 0.0
            
        var_percentile = 1 - self.confidence_level
        return float(np.percentile(returns, var_percentile * 100))
        
    def _calculate_expected_shortfall(self, returns: np.ndarray) -> float:
        """
        Calcula Expected Shortfall (Conditional VaR)
        """
        if len(returns) == 0:
            return 0.0
            
        var = self._calculate_var(returns)
        return float(returns[returns <= var].mean())
        
    def _aggregate_greeks(self, positions: List[OptionContract]) -> Dict[str, float]:
        """
        Agrega os Greeks do portfolio
        """
        total_delta: float = 0.0
        total_gamma: float = 0.0
        total_theta: float = 0.0
        total_vega: float = 0.0
        
        for position in positions:
            # Assumindo que os Greeks estão armazenados no objeto OptionContract
            if hasattr(position, 'greeks'):
                total_delta += position.greeks.get('delta', 0.0)
                total_gamma += position.greeks.get('gamma', 0.0)
                total_theta += position.greeks.get('theta', 0.0)
                total_vega += position.greeks.get('vega', 0.0)
        
        return {
            'delta': total_delta,
            'gamma': total_gamma,
            'theta': total_theta,
            'vega': total_vega
        }
        
    def _run_stress_tests(self, positions: List[OptionContract]) -> Dict[str, float]:
        """
        Executa cenários de stress test
        """
        results: Dict[str, float] = {}
        
        # Cenário de queda de 20%
        down_scenario = self._calculate_portfolio_value(positions, price_change=-0.20)
        results['down_20_percent'] = down_scenario
        
        # Cenário de alta de 20%
        up_scenario = self._calculate_portfolio_value(positions, price_change=0.20)
        results['up_20_percent'] = up_scenario
        
        # Cenário de volatilidade dobrada
        vol_scenario = self._calculate_portfolio_value(positions, vol_change=1.0)
        results['double_volatility'] = vol_scenario
        
        return results
        
    def _calculate_portfolio_value(self, positions: List[OptionContract], 
                                 price_change: float = 0.0,
                                 vol_change: float = 0.0) -> float:
        """
        Calcula o valor do portfolio em um cenário específico
        """
        total_value: float = 0.0
        
        for position in positions:
            # Ajusta o preço do ativo subjacente
            new_price = position.current_price * (1 + price_change)
            
            # Recalcula o valor da opção com os novos parâmetros
            # Esta é uma simplificação - em um caso real você usaria
            # um modelo de precificação completo como Black-Scholes
            value_change = (
                position.greeks.get('delta', 0.0) * new_price +
                position.greeks.get('gamma', 0.0) * new_price * new_price * 0.5 +
                position.greeks.get('vega', 0.0) * vol_change
            )
            
            total_value += value_change
            
        return total_value
        
    def _calculate_correlation(self, positions: List[OptionContract]) -> np.ndarray:
        """
        Calcula matriz de correlação entre as posições
        """
        n = len(positions)
        correlation_matrix = np.ones((n, n))
        
        # Em um caso real, você usaria dados históricos para calcular
        # as correlações entre os ativos subjacentes
        # Esta é uma simplificação
        for i in range(n):
            for j in range(i+1, n):
                correlation = 0.5  # Valor exemplo
                correlation_matrix[i,j] = correlation
                correlation_matrix[j,i] = correlation
                
        return correlation_matrix
