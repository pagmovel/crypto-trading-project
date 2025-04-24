import asyncio
import ccxt.async_support as ccxt
import platform
import logging
from typing import List, Dict, Any
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

class CCXTService:
    def __init__(self, simulation_mode: bool = True) -> None:
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        self.simulation_mode = simulation_mode
        if not simulation_mode:
            self.exchange = ccxt.binance({
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'option'
                }
            })
    
    def _generate_simulated_options(self, symbol: str, expiry: datetime) -> List[Dict[str, Any]]:
        """Gera dados simulados de opções para desenvolvimento e testes"""
        base_price = 45000.0  # Preço base para BTC
        if symbol.startswith('ETH'):
            base_price = 3000.0
        
        # Gera strikes em torno do preço base
        strikes = [base_price * (0.8 + i * 0.1) for i in range(5)]  # 5 strikes
        
        options = []
        for strike in strikes:
            # Opção de compra
            call = {
                'symbol': f'{symbol}-{int(strike)}-C',
                'strike': strike,
                'expiry': expiry.timestamp(),
                'type': 'CALL',
                'underlying': symbol,
                'price': max(0.001, base_price * 0.1 * np.random.random())
            }
            options.append(call)
            
            # Opção de venda
            put = {
                'symbol': f'{symbol}-{int(strike)}-P',
                'strike': strike,
                'expiry': expiry.timestamp(),
                'type': 'PUT',
                'underlying': symbol,
                'price': max(0.001, base_price * 0.1 * np.random.random())
            }
            options.append(put)
            
        return options
    
    async def fetch_options_data(self, symbol: str, expiry: datetime) -> List[Dict[str, Any]]:
        try:
            if self.simulation_mode:
                logger.info("Usando modo de simulação para dados de opções")
                if symbol == "BTC/USD":
                    symbol = "BTC/USDT"
                symbol_base = symbol.split('/')[0]
                options = self._generate_simulated_options(symbol_base, expiry)
                logger.info(f"Gerados {len(options)} contratos de opções simulados")
                return options
            
            logger.info(f"Carregando mercados para {symbol}")
            markets = await self.exchange.load_markets()
            logger.info(f"Mercados carregados: {len(markets)} pares disponíveis")
            
            market_types = set(market['type'] for market in markets.values())
            logger.info(f"Tipos de mercado disponíveis: {market_types}")
            
            options = []
            symbol_base = symbol.split('/')[0]
            
            if symbol == "BTC/USD":
                symbol = "BTC/USDT"
                logger.info(f"Convertendo par para {symbol}")
            
            for market_id, market in markets.items():
                if market['type'] == 'option' and market['base'] == symbol_base:
                    logger.info(f"Encontrado mercado de opções: {market_id}")
                    market_expiry = datetime.fromtimestamp(market['expiry'])
                    if market_expiry.date() == expiry.date():
                        options.append(market)
                        logger.info(f"Opção adicionada: strike={market.get('strike')}, tipo={market.get('type')}")
            
            logger.info(f"Total de opções encontradas: {len(options)}")
            return options
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados de opções: {str(e)}", exc_info=True)
            return []
    
    async def get_underlying_price(self, symbol: str) -> float:
        try:
            if self.simulation_mode:
                if symbol.startswith('BTC'):
                    return 45000.0
                elif symbol.startswith('ETH'):
                    return 3000.0
                return 100.0
                
            # Converte para USDT se necessário
            if symbol.endswith('/USD'):
                symbol = symbol.replace('/USD', '/USDT')
                
            logger.info(f"Buscando preço para {symbol}")
            ticker = await self.exchange.fetch_ticker(symbol)
            price = ticker['last'] if ticker and 'last' in ticker else 0.0
            logger.info(f"Preço obtido: {price}")
            return price
        except Exception as e:
            logger.error(f"Erro ao buscar preço do ativo subjacente: {str(e)}", exc_info=True)
            return 0.0
    
    async def close(self) -> None:
        if not self.simulation_mode and hasattr(self, 'exchange'):
            await self.exchange.close()
