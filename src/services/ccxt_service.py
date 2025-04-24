from typing import Dict, Any, List, Optional
import ccxt
import ccxt.async_support as ccxt_async
from datetime import datetime
import os
from dotenv import load_dotenv

from models.market_model import OptionContract, Exchange

class CCXTService:
    def __init__(self) -> None:
        load_dotenv()
        self.exchange: ccxt.Exchange = self._initialize_exchange()
        self.async_exchange: ccxt.async_support.Exchange = self._initialize_async_exchange()
        
    def _initialize_exchange(self) -> ccxt.Exchange:
        exchange_id = os.getenv("EXCHANGE_ID", "deribit")
        api_key = os.getenv("API_KEY")
        secret = os.getenv("API_SECRET")
        
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
        })
        return exchange
        
    def _initialize_async_exchange(self) -> ccxt.async_support.Exchange:
        exchange_id = os.getenv("EXCHANGE_ID", "deribit")
        api_key = os.getenv("API_KEY")
        secret = os.getenv("API_SECRET")
        
        exchange_class = getattr(ccxt_async, exchange_id)
        exchange = exchange_class({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
        })
        return exchange

    async def fetch_options_data(self, symbol: str, expiry: datetime) -> List[Dict[str, Any]]:
        try:
            markets = await self.async_exchange.load_markets()
            options = []
            
            for market_id in markets:
                market = markets[market_id]
                if (market['type'] == 'option' and 
                    market['base'] == symbol and
                    market['expiry'] == expiry.timestamp() * 1000):
                    
                    ticker = await self.async_exchange.fetch_ticker(market_id)
                    options.append({
                        'symbol': market_id,
                        'strike': market['strike'],
                        'type': market['option_type'],
                        'expiry': expiry,
                        'price': ticker['last'] if ticker['last'] else 0,
                        'underlying': market['base'],
                    })
                    
            return options
            
        except Exception as e:
            print(f"Erro ao buscar dados de opções: {e}")
            return []

    async def get_underlying_price(self, symbol: str) -> float:
        try:
            ticker = await self.async_exchange.fetch_ticker(symbol)
            return float(ticker['last'])
        except Exception as e:
            print(f"Erro ao buscar preço do ativo subjacente: {e}")
            return 0.0

    async def get_option_price(self, symbol: str) -> float:
        try:
            ticker = await self.async_exchange.fetch_ticker(symbol)
            return float(ticker['last'])
        except Exception as e:
            print(f"Erro ao buscar preço da opção: {e}")
            return 0.0
            
    async def close(self) -> None:
        await self.async_exchange.close()
