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

    def _configure_3d_axes(self):
        """Configura os eixos para gráficos 3D"""
        return {
            "xaxis": {"title": "Preço de Exercício"},
            "yaxis": {"title": "Tempo até Vencimento"},
            "zaxis": {"title": "Valor"}
        }

    def plot_volatility_surface(self, options: List[OptionContract], analysis: Dict[str, OptionAnalysis]) -> None:
        # Separa calls e puts
        calls = [opt for opt in options if opt.is_call]
        puts = [opt for opt in options if not opt.is_call]
        
        # Cria o gráfico com subplots
        fig = sp.make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'scene'}, {'type': 'scene'}]],
            subplot_titles=('Volatilidade Implícita - Calls', 'Volatilidade Implícita - Puts')
        )
        
        # Plota superfície para calls
        if calls:
            strikes_c = [opt.strike_price for opt in calls]
            expiries_c = [opt.time_to_expiry for opt in calls]
            vols_c = [analysis[opt.contract_id].implied_volatility for opt in calls]
            
            fig.add_trace(
                go.Scatter3d(
                    x=strikes_c,
                    y=expiries_c,
                    z=vols_c,
                    mode='markers+lines',
                    name='Calls',
                    marker=dict(
                        size=4,
                        color=vols_c,
                        colorscale='Viridis',
                        showscale=True
                    )
                ),
                row=1, col=1
            )
        
        # Plota superfície para puts
        if puts:
            strikes_p = [opt.strike_price for opt in puts]
            expiries_p = [opt.time_to_expiry for opt in puts]
            vols_p = [analysis[opt.contract_id].implied_volatility for opt in puts]
            
            fig.add_trace(
                go.Scatter3d(
                    x=strikes_p,
                    y=expiries_p,
                    z=vols_p,
                    mode='markers+lines',
                    name='Puts',
                    marker=dict(
                        size=4,
                        color=vols_p,
                        colorscale='Viridis',
                        showscale=True
                    )
                ),
                row=1, col=2
            )

        # Atualiza os layouts das cenas
        fig.update_layout(
            scene=self._configure_3d_axes(),
            scene2=self._configure_3d_axes(),
            title='Superfície de Volatilidade',
            showlegend=True,
            **self.default_layout
        )
        
        fig.show()
    
    def plot_greeks_surface(self, options: List[OptionContract], analysis: Dict[str, OptionAnalysis]) -> None:
        # Separa calls e puts para cada Greek
        calls = [opt for opt in options if opt.is_call]
        puts = [opt for opt in options if not opt.is_call]
        
        # Cria subplots para cada Greek
        fig = sp.make_subplots(
            rows=2, cols=2,
            specs=[[{'type': 'scene'}, {'type': 'scene'}],
                  [{'type': 'scene'}, {'type': 'scene'}]],
            subplot_titles=('Delta', 'Gamma', 'Theta', 'Vega')
        )
        
        greek_positions = {
            'delta': (1, 1),
            'gamma': (1, 2),
            'theta': (2, 1),
            'vega': (2, 2)
        }
        
        for greek, (row, col) in greek_positions.items():
            # Dados para calls
            if calls:
                strikes_c = [opt.strike_price for opt in calls]
                expiries_c = [opt.time_to_expiry for opt in calls]
                values_c = [analysis[opt.contract_id].greeks[greek] for opt in calls]
                
                fig.add_trace(
                    go.Scatter3d(
                        x=strikes_c,
                        y=expiries_c,
                        z=values_c,
                        mode='markers+lines',
                        name=f'Calls - {greek.capitalize()}',
                        marker=dict(
                            size=4,
                            color=values_c,
                            colorscale='Viridis',
                            showscale=True
                        )
                    ),
                    row=row, col=col
                )
            
            # Dados para puts
            if puts:
                strikes_p = [opt.strike_price for opt in puts]
                expiries_p = [opt.time_to_expiry for opt in puts]
                values_p = [analysis[opt.contract_id].greeks[greek] for opt in puts]
                
                fig.add_trace(
                    go.Scatter3d(
                        x=strikes_p,
                        y=expiries_p,
                        z=values_p,
                        mode='markers+lines',
                        name=f'Puts - {greek.capitalize()}',
                        marker=dict(
                            size=4,
                            color=values_p,
                            colorscale='Viridis',
                            showscale=True
                        )
                    ),
                    row=row, col=col
                )

        # Atualiza o layout com as configurações das cenas
        layout = {
            **self.default_layout,
            "title": 'Superfície de Greeks',
            "showlegend": True,
            "height": 1000,
            "scene": self._configure_3d_axes(),
            "scene2": self._configure_3d_axes(),
            "scene3": self._configure_3d_axes(),
            "scene4": self._configure_3d_axes()
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
            name='Payoff Bruto',
            line=dict(color='#00ff00', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=prices, 
            y=net_payoffs, 
            name='Payoff Líquido',
            line=dict(color='#ff0000', width=2)
        ))
        
        # Adiciona linha vertical no preço de exercício
        fig.add_vline(
            x=option.strike_price,
            line_dash="dash",
            annotation_text=f"Strike: {option.strike_price:,.2f}"
        )
        
        layout = {
            **self.default_layout,
            "title": f'Payoff da Opção {option.symbol}',
            "xaxis_title": 'Preço do Ativo',
            "yaxis_title": 'Payoff',
            "showlegend": True,
            "hovermode": 'x unified'
        }
        fig.update_layout(**layout)
        fig.show()
