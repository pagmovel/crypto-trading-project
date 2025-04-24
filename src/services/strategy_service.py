from typing import List, Dict, Any, Optional
from datetime import datetime
from models.market_model import OptionContract, OptionAnalysis
from services.ccxt_service import CCXTService

class StrategyService:
    def __init__(self) -> None:
        self.ccxt_service = CCXTService()

    async def iron_condor(self, symbol: str, expiry: datetime, width: float = 0.1) -> List[OptionContract]:
        """
        Cria uma estratégia Iron Condor para o símbolo e data de expiração especificados
        """
        spot_price = await self.ccxt_service.get_underlying_price(symbol)
        
        # Definir strikes (convertendo para float explicitamente)
        lower_put = float(spot_price * (1 - width))
        upper_put = float(spot_price * (1 - width/2))
        lower_call = float(spot_price * (1 + width/2))
        upper_call = float(spot_price * (1 + width))
        
        # Criar contratos
        contracts = [
            OptionContract(
                symbol=symbol,
                strike_price=lower_put,
                expiry=expiry,
                contract_id=f"{symbol}-P-{lower_put}",
                underlying=symbol,
                is_call=False,
                current_price=0.0
            ),
            OptionContract(
                symbol=symbol,
                strike_price=upper_put,
                expiry=expiry,
                contract_id=f"{symbol}-P-{upper_put}",
                underlying=symbol,
                is_call=False,
                current_price=0.0
            ),
            OptionContract(
                symbol=symbol,
                strike_price=lower_call,
                expiry=expiry,
                contract_id=f"{symbol}-C-{lower_call}",
                underlying=symbol,
                is_call=True,
                current_price=0.0
            ),
            OptionContract(
                symbol=symbol,
                strike_price=upper_call,
                expiry=expiry,
                contract_id=f"{symbol}-C-{upper_call}",
                underlying=symbol,
                is_call=True,
                current_price=0.0
            )
        ]
        
        return contracts

    async def butterfly(self, symbol: str, expiry: datetime, width: float = 0.05) -> List[OptionContract]:
        """
        Cria uma estratégia Butterfly para o símbolo e data de expiração especificados
        """
        spot_price = await self.ccxt_service.get_underlying_price(symbol)
        
        # Definir strikes (convertendo para float explicitamente)
        lower_strike = float(spot_price * (1 - width))
        middle_strike = float(spot_price)
        upper_strike = float(spot_price * (1 + width))
        
        # Criar contratos
        contracts = [
            OptionContract(
                symbol=symbol,
                strike_price=lower_strike,
                expiry=expiry,
                contract_id=f"{symbol}-C-{lower_strike}",
                underlying=symbol,
                is_call=True,
                current_price=0.0
            ),
            OptionContract(
                symbol=symbol,
                strike_price=middle_strike,
                expiry=expiry,
                contract_id=f"{symbol}-C-{middle_strike}",
                underlying=symbol,
                is_call=True,
                current_price=0.0
            ),
            OptionContract(
                symbol=symbol,
                strike_price=upper_strike,
                expiry=expiry,
                contract_id=f"{symbol}-C-{upper_strike}",
                underlying=symbol,
                is_call=True,
                current_price=0.0
            )
        ]
        
        return contracts

    async def calculate_strategy_metrics(self, positions: List[OptionContract]) -> Dict[str, Any]:
        """
        Calcula métricas para uma estratégia, incluindo gregas e custo total
        """
        total_cost = 0.0
        total_delta = 0.0
        total_gamma = 0.0
        
        for position in positions:
            # Atualizar preço atual
            quote = await self.ccxt_service.get_option_quote(position.contract_id)
            total_cost += quote['price']
            
            # Calcular gregas
            delta = quote.get('delta', 0.0)
            gamma = quote.get('gamma', 0.0)
            
            total_delta += delta
            total_gamma += gamma
        
        return {
            'total_cost': total_cost,
            'greeks': {
                'delta': total_delta,
                'gamma': total_gamma
            }
        }
