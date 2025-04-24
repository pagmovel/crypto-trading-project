from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from models.market_model import OptionContract

class VisualizationService:
    def __init__(self) -> None:
        self.default_layout = {
            "template": "plotly_dark",
            "showlegend": True,
        }

    def plot_volatility_surface(self, options: List[OptionContract], analysis: Dict[str, Any]) -> None:
        strikes = [opt.strike_price for opt in options]
        expiries = [opt.expiry.strftime("%Y-%m-%d") for opt in options]
        vols = [analysis[opt.contract_id]["implied_volatility"] for opt in options]
        
        fig = go.Figure(data=[
            go.Surface(
                x=strikes,
                y=expiries,
                z=vols,
                colorscale="Viridis"
            )
        ])
        
        fig.update_layout(
            title="Superfície de Volatilidade",
            scene={
                "xaxis_title": "Strike",
                "yaxis_title": "Vencimento",
                "zaxis_title": "Volatilidade Implícita"
            },
            **self.default_layout
        )
        fig.show()

    def plot_greeks_surface(self, options: List[OptionContract], analysis: Dict[str, Any]) -> None:
        strikes = [opt.strike_price for opt in options]
        expiries = [opt.expiry.strftime("%Y-%m-%d") for opt in options]
        
        for greek in ["delta", "gamma", "theta", "vega"]:
            values = [analysis[opt.contract_id]["greeks"][greek] for opt in options]
            
            fig = go.Figure(data=[
                go.Surface(
                    x=strikes,
                    y=expiries,
                    z=values,
                    colorscale="Viridis"
                )
            ])
            
            fig.update_layout(
                title=f"Superfície de {greek.capitalize()}",
                scene={
                    "xaxis_title": "Strike",
                    "yaxis_title": "Vencimento",
                    "zaxis_title": greek.capitalize()
                },
                **self.default_layout
            )
            fig.show()

    def plot_option_payoff(self, option: OptionContract, price_range: tuple[float, float], analysis: Dict[str, Any]) -> None:
        prices = np.linspace(price_range[0], price_range[1], 100)
        payoffs = []
        
        for price in prices:
            if option.is_call:
                payoff = max(0, price - option.strike_price) - option.current_price
            else:
                payoff = max(0, option.strike_price - price) - option.current_price
            payoffs.append(payoff)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=prices,
            y=payoffs,
            mode="lines",
            name=f"{option.contract_id} Payoff"
        ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.add_vline(x=option.strike_price, line_dash="dash", line_color="gray")
        
        fig.update_layout(
            title=f"Payoff da Opção {option.contract_id}",
            xaxis_title="Preço do Ativo Subjacente",
            yaxis_title="Lucro/Prejuízo",
            **self.default_layout
        )
        fig.show()
