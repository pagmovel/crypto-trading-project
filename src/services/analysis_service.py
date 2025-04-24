import numpy as np
import pandas as pd
from models.market_model import OptionContract
from typing import Dict, Any, Optional
from scipy.stats import norm
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Greeks:
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float = 0.0

class AnalysisService:
    def __init__(self) -> None:
        self.risk_free_rate = 0.05  # Taxa livre de risco padrão
        
    def calculate_implied_volatility(self, strike: float, spot: float, time_to_expiry: float, is_call: bool) -> float:
        # Implementação do método de Newton-Raphson para calcular volatilidade implícita
        target_price = spot  # Preço alvo (mercado)
        vol = 0.5  # Estimativa inicial
        MAX_ITERATIONS = 100
        PRECISION = 0.00001
        
        for i in range(MAX_ITERATIONS):
            price = self._black_scholes_price(spot, strike, time_to_expiry, vol, is_call)
            diff = target_price - price
            
            if abs(diff) < PRECISION:
                return float(vol)
                
            vega = self._calculate_vega(spot, strike, time_to_expiry, vol)
            if vega == 0:
                return float(vol)
                
            vol = vol + diff / vega
            
            if vol <= 0:
                return 0.0001
                
        return float(vol)
    
    def calculate_greeks(self, spot: float, strike: float, time_to_expiry: float, 
                        volatility: float, is_call: bool) -> Greeks:
        # Cálculo dos Greeks usando Black-Scholes
        if volatility <= 0:
            volatility = 0.0001
            
        sqrt_t = np.sqrt(time_to_expiry)
        d1 = (np.log(spot/strike) + (self.risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * sqrt_t)
        d2 = d1 - volatility * sqrt_t
        
        # Delta
        if is_call:
            delta = float(norm.cdf(d1))
        else:
            delta = float(norm.cdf(d1) - 1)
            
        # Gamma
        gamma = float(norm.pdf(d1) / (spot * volatility * sqrt_t))
        
        # Theta
        theta_term1 = -(spot * norm.pdf(d1) * volatility) / (2 * sqrt_t)
        if is_call:
            theta = float(theta_term1 - self.risk_free_rate * strike * np.exp(-self.risk_free_rate * time_to_expiry) * norm.cdf(d2))
        else:
            theta = float(theta_term1 + self.risk_free_rate * strike * np.exp(-self.risk_free_rate * time_to_expiry) * norm.cdf(-d2))
        
        # Vega
        vega = float(spot * sqrt_t * norm.pdf(d1))
        
        return Greeks(delta=delta, gamma=gamma, theta=theta, vega=vega)
    
    def _black_scholes_price(self, spot: float, strike: float, time_to_expiry: float, 
                          volatility: float, is_call: bool) -> float:
        sqrt_t = np.sqrt(time_to_expiry)
        d1 = (np.log(spot/strike) + (self.risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * sqrt_t)
        d2 = d1 - volatility * sqrt_t
        
        if is_call:
            price = spot * norm.cdf(d1) - strike * np.exp(-self.risk_free_rate * time_to_expiry) * norm.cdf(d2)
        else:
            price = strike * np.exp(-self.risk_free_rate * time_to_expiry) * norm.cdf(-d2) - spot * norm.cdf(-d1)
            
        return float(price)
    
    def _calculate_vega(self, spot: float, strike: float, time_to_expiry: float, 
                     volatility: float) -> float:
        sqrt_t = np.sqrt(time_to_expiry)
        d1 = (np.log(spot/strike) + (self.risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * sqrt_t)
        return float(spot * sqrt_t * norm.pdf(d1))
    
    def _calculate_time_to_expiry(self, expiry: datetime) -> float:
        now = datetime.now()
        return (expiry - now).total_seconds() / (365 * 24 * 60 * 60)
