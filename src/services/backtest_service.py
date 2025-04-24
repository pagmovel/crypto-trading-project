from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from dataclasses import dataclass

from models.market_model import OptionContract, MarketData

@dataclass
class BacktestResult:
    trades: List[Dict[str, Any]]
    pnl: List[float]
    equity_curve: List[float]
    metrics: Dict[str, float]
    positions: List[Dict[str, Any]]

class BacktestService:
    def __init__(self) -> None:
        self.initial_capital: float = 10000.0
        self.position: float = 0.0
        self.cash: float = self.initial_capital
        self.equity: List[float] = [self.initial_capital]
        self.trades: List[Dict[str, Any]] = []
        self.positions: List[Dict[str, Any]] = []

    def run_backtest(self, data: List[MarketData], strategy_fn: callable) -> BacktestResult:
        """
        Executa o backtest usando os dados históricos e a função de estratégia fornecida
        """
        for i, candle in enumerate(data):
            signal = strategy_fn(data[:i+1])
            if signal != 0:
                self._execute_trade(signal, candle.price, candle.timestamp)

        return self._generate_results()

    def _execute_trade(self, signal: float, price: float, timestamp: datetime) -> None:
        """
        Executa uma operação de compra ou venda
        """
        if signal > 0:  # Compra
            if self.position <= 0:
                qty = min(signal, self.cash / price)
                cost = qty * price
                if self._validate_trade(qty, cost):
                    self.position = qty
                    self.cash -= cost
                    self._record_trade("BUY", qty, price, timestamp)

        elif signal < 0:  # Venda
            if self.position >= 0:
                qty = min(abs(signal), self.position)
                revenue = qty * price
                if self._validate_trade(qty, revenue):
                    self.position = -qty
                    self.cash += revenue
                    self._record_trade("SELL", qty, price, timestamp)

        # Atualiza equity
        current_equity = self.cash + (self.position * price)
        self.equity.append(current_equity)

    def _validate_trade(self, quantity: float, value: float) -> bool:
        """
        Valida se uma operação pode ser executada
        """
        if quantity <= 0:
            return False
            
        if value > self.cash:
            return False
            
        return True

    def _record_trade(self, side: str, quantity: float, price: float, timestamp: datetime) -> None:
        """
        Registra uma operação executada
        """
        trade = {
            "timestamp": timestamp,
            "side": side,
            "quantity": quantity,
            "price": price,
            "value": quantity * price
        }
        self.trades.append(trade)
        
        position = {
            "timestamp": timestamp,
            "position": self.position,
            "cash": self.cash,
            "equity": self.equity[-1]
        }
        self.positions.append(position)

    def _calculate_metrics(self) -> Dict[str, float]:
        """
        Calcula métricas de performance do backtest
        """
        returns = pd.Series(self.equity).pct_change().dropna()
        
        total_return = (self.equity[-1] - self.initial_capital) / self.initial_capital
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if len(returns) > 0 else 0
        max_drawdown = self._calculate_max_drawdown()
        win_rate = self._calculate_win_rate()
        
        return {
            "total_return": float(total_return),
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "win_rate": float(win_rate)
        }

    def _calculate_max_drawdown(self) -> float:
        """
        Calcula o máximo drawdown
        """
        equity_series = pd.Series(self.equity)
        cummax = equity_series.cummax()
        drawdown = (cummax - equity_series) / cummax
        return float(drawdown.max())

    def _calculate_win_rate(self) -> float:
        """
        Calcula o percentual de trades vencedores
        """
        if not self.trades:
            return 0.0
            
        pnl = []
        for trade in self.trades:
            if trade["side"] == "BUY":
                pnl.append(-trade["value"])
            else:
                pnl.append(trade["value"])
                
        winning_trades = sum(1 for p in pnl if p > 0)
        return float(winning_trades / len(pnl))

    def _generate_results(self) -> BacktestResult:
        """
        Gera o resultado final do backtest
        """
        return BacktestResult(
            trades=self.trades,
            pnl=[t["value"] for t in self.trades],
            equity_curve=self.equity,
            metrics=self._calculate_metrics(),
            positions=self.positions
        )
