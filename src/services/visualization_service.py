import plotly.graph_objects as go
import plotly.subplots as sp
import numpy as np
from typing import List, Dict, Any
from models.market_model import OptionContract, OptionAnalysis

class VisualizationService:
    def __init__(self) -> None:
        self.default_layout = {
            "template": "plotly_dark",
            "margin": dict(l=50, r=50, t=50, b=50)
        }

    def plot_volatility_surface(self, options: List[OptionContract], analysis: Dict[str, OptionAnalysis]) -> None:
        # Separa calls e puts
        calls = [opt for opt in options if opt.is_call]
        puts = [opt for opt in options if not opt.is_call]
        
        # Ordena as opções por strike para criar linhas contínuas
        calls = sorted(calls, key=lambda x: x.strike_price)
        puts = sorted(puts, key=lambda x: x.strike_price)
        
        # Cria o gráfico
        fig = go.Figure()
        
        if calls:
            strikes_c = [opt.strike_price for opt in calls]
            vols_c = [analysis[opt.contract_id].implied_volatility * 100 for opt in calls]  # Converte para porcentagem
            
            fig.add_trace(
                go.Scatter(
                    x=strikes_c,
                    y=vols_c,
                    mode="lines+markers",
                    name="Calls",
                    line=dict(color="#00ff00", width=2),
                    marker=dict(size=8)
                )
            )
        
        if puts:
            strikes_p = [opt.strike_price for opt in puts]
            vols_p = [analysis[opt.contract_id].implied_volatility * 100 for opt in puts]  # Converte para porcentagem
            
            fig.add_trace(
                go.Scatter(
                    x=strikes_p,
                    y=vols_p,
                    mode="lines+markers",
                    name="Puts",
                    line=dict(color="#ff0000", width=2),
                    marker=dict(size=8)
                )
            )

        # Atualiza o layout
        layout = {
            **self.default_layout,
            "title": "Smile de Volatilidade",
            "xaxis_title": "Preço de Exercício",
            "yaxis_title": "Volatilidade Implícita (%)",
            "showlegend": True,
            "hovermode": "x unified",
            "yaxis": dict(
                tickformat=".1f",  # Formato com 1 casa decimal
                ticksuffix="%"     # Adiciona % nos valores do eixo Y
            )
        }
        fig.update_layout(**layout)
        fig.show()

    def plot_greeks_surface(self, options: List[OptionContract], analysis: Dict[str, OptionAnalysis]) -> None:
        # Separa calls e puts
        calls = [opt for opt in options if opt.is_call]
        puts = [opt for opt in options if not opt.is_call]
        
        # Cria subplots para cada Greek
        fig = sp.make_subplots(
            rows=2, cols=2,
            subplot_titles=("Delta", "Gamma", "Theta", "Vega")
        )
        
        greek_positions = {
            "delta": (1, 1),
            "gamma": (1, 2),
            "theta": (2, 1),
            "vega": (2, 2)
        }
        
        for greek, (row, col) in greek_positions.items():
            if calls:
                strikes_c = [opt.strike_price for opt in calls]
                values_c = [analysis[opt.contract_id].greeks[greek] for opt in calls]
                
                fig.add_trace(
                    go.Scatter(
                        x=strikes_c,
                        y=values_c,
                        mode="lines+markers",
                        name=f"Calls - {greek.capitalize()}",
                        line=dict(color="#00ff00", width=2),
                        marker=dict(size=8)
                    ),
                    row=row, col=col
                )
            
            if puts:
                strikes_p = [opt.strike_price for opt in puts]
                values_p = [analysis[opt.contract_id].greeks[greek] for opt in puts]
                
                fig.add_trace(
                    go.Scatter(
                        x=strikes_p,
                        y=values_p,
                        mode="lines+markers",
                        name=f"Puts - {greek.capitalize()}",
                        line=dict(color="#ff0000", width=2),
                        marker=dict(size=8)
                    ),
                    row=row, col=col
                )

        # Atualiza o layout
        layout = {
            **self.default_layout,
            "title": "Greeks vs Strike",
            "showlegend": True,
            "height": 800,
            "xaxis_title": "Preço de Exercício",
            "xaxis2_title": "Preço de Exercício",
            "xaxis3_title": "Preço de Exercício",
            "xaxis4_title": "Preço de Exercício",
            "yaxis_title": "Delta",
            "yaxis2_title": "Gamma",
            "yaxis3_title": "Theta",
            "yaxis4_title": "Vega"
        }
        fig.update_layout(**layout)
        fig.show()

    def plot_option_payoff(self, option: OptionContract, price_range: tuple[float, float], analysis: Dict[str, OptionAnalysis]) -> None:
        # Gera pontos para o gráfico
        prices = np.linspace(price_range[0], price_range[1], 100)
        if option.is_call:
            payoffs = np.maximum(0, prices - option.strike_price)
        else:
            payoffs = np.maximum(0, option.strike_price - prices)
        
        # Adiciona o prêmio da opção
        current_price = analysis[option.contract_id].theoretical_price
        net_payoffs = payoffs - current_price
        
        # Cria o gráfico
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=prices, 
            y=payoffs, 
            name="Payoff Bruto",
            line=dict(color="#00ff00", width=2)
        ))
        fig.add_trace(go.Scatter(
            x=prices, 
            y=net_payoffs, 
            name="Payoff Líquido",
            line=dict(color="#ff0000", width=2)
        ))
        
        # Adiciona linha vertical no preço de exercício
        fig.add_vline(
            x=option.strike_price,
            line_dash="dash",
            annotation_text=f"Strike: {option.strike_price:,.2f}"
        )
        
        layout = {
            **self.default_layout,
            "title": f"Payoff da Opção {option.symbol}",
            "xaxis_title": "Preço do Ativo",
            "yaxis_title": "Payoff",
            "showlegend": True,
            "hovermode": "x unified"
        }
        fig.update_layout(**layout)
        fig.show()
