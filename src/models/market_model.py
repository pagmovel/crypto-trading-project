from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal


@dataclass
class OptionContract:
    symbol: str
    strike_price: float
    expiry: datetime
    contract_id: str
    underlying: str
    is_call: bool
    current_price: float = 0.0
    volume: float = 0.0
    open_interest: float = 0.0
    
    @property
    def time_to_expiry(self) -> float:
        now = datetime.now()
        return (self.expiry - now).total_seconds() / (365 * 24 * 60 * 60)


@dataclass
class OptionAnalysis:
    contract: OptionContract
    implied_volatility: float
    theoretical_price: float
    intrinsic_value: float
    extrinsic_value: float
    greeks: dict[str, float]


@dataclass
class MarketData:
    timestamp: datetime
    price: float
    volume: float
    high: float
    low: float
    open: float
    close: float


@dataclass
class Exchange:
    name: str
    api_key: Optional[str] = None
    secret: Optional[str] = None
    testnet: bool = False
