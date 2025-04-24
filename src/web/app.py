from typing import List, Dict, Any, Tuple, Optional, Union
import dash
from dash import html, dcc
from dash._callback import Output, Input
from dash._utils import Options
import dash_bootstrap_components as dbc  # type: ignore
import plotly.graph_objects as go
from datetime import datetime, timedelta
import asyncio

from services.ccxt_service import CCXTService
from services.analysis_service import AnalysisService
from services.visualization_service import VisualizationService
from services.strategy_service import StrategyService
from models.market_model import OptionContract, OptionAnalysis

# Inicializa app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Serviços
ccxt_service = CCXTService()
analysis_service = AnalysisService()
visualization_service = VisualizationService()
strategy_service = StrategyService()

# Estado global
positions: List[OptionContract] = []
analysis_results: Dict[str, OptionAnalysis] = {}

# Layout
symbol_options: List[Options] = [
    {'label': 'BTC/USD', 'value': 'BTC/USD'},
    {'label': 'ETH/USD', 'value': 'ETH/USD'}
]

strategy_options: List[Options] = [
    {'label': 'Iron Condor', 'value': 'iron_condor'},
    {'label': 'Butterfly', 'value': 'butterfly'}
]

app.layout = dbc.Container([
    html.H1("Options Analysis Dashboard", className="my-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Market Data", className="card-title"),
                    dcc.Dropdown(
                        id='symbol-dropdown',
                        options=symbol_options,
                        value='BTC/USD'
                    ),
                    dcc.Graph(id='price-chart')
                ])
            ])
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Option Chain", className="card-title"),
                    html.Div(id='option-chain')
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Greeks", className="card-title"),
                    dcc.Graph(id='greeks-chart')
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Strategy Builder", className="card-title"),
                    dcc.Dropdown(
                        id='strategy-dropdown',
                        options=strategy_options,
                        value='iron_condor'
                    ),
                    html.Div(id='strategy-params')
                ])
            ])
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Strategy Analysis", className="card-title"),
                    html.Div(id='strategy-analysis')
                ])
            ])
        ], width=6)
    ])
])

@app.callback(
    [Output('price-chart', 'figure'),
     Output('option-chain', 'children')],
    [Input('symbol-dropdown', 'value')]
)
async def update_market_data(symbol: str) -> Tuple[go.Figure, html.Table]:
    """
    Atualiza dados de mercado quando o símbolo muda
    """
    expiry = datetime.now() + timedelta(days=30)
    
    try:
        # Busca dados de opções
        options_data = await ccxt_service.fetch_options_data(symbol, expiry)
        global positions
        positions = []
        
        for data in options_data:
            option = OptionContract(
                symbol=data["symbol"],
                strike_price=float(data["strike"]),
                expiry=data["expiry"],
                contract_id=data["symbol"],
                underlying=data["underlying"],
                is_call=data["type"].upper() == "CALL",
                current_price=float(data["price"])
            )
            positions.append(option)
        
        # Cria gráfico de preço
        spot_price = await ccxt_service.get_underlying_price(symbol)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[datetime.now()], y=[spot_price], mode='lines+markers'))
        
        # Cria tabela de opções
        option_table = html.Table([
            html.Thead([
                html.Tr([
                    html.Th("Strike"),
                    html.Th("Type"),
                    html.Th("Price"),
                    html.Th("Expiry")
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(option.strike_price),
                    html.Td("Call" if option.is_call else "Put"),
                    html.Td(option.current_price),
                    html.Td(option.expiry.strftime("%Y-%m-%d"))
                ]) for option in positions
            ])
        ])
        
        return fig, option_table
        
    except Exception as e:
        print(f"Erro ao atualizar dados de mercado: {e}")
        return go.Figure(), html.Div("Erro ao carregar dados")

@app.callback(
    Output('greeks-chart', 'figure'),
    [Input('symbol-dropdown', 'value')]
)
def update_greeks(symbol: str) -> go.Figure:
    """
    Atualiza gráfico dos Greeks quando o símbolo muda
    """
    try:
        if not positions:
            return go.Figure()
            
        fig = visualization_service.plot_greeks_surface(positions, analysis_results)
        return fig
        
    except Exception as e:
        print(f"Erro ao atualizar Greeks: {e}")
        return go.Figure()

@app.callback(
    [Output('strategy-params', 'children'),
     Output('strategy-analysis', 'children')],
    [Input('strategy-dropdown', 'value')]
)
async def update_strategy(strategy: str) -> Tuple[html.Div, html.Div]:
    """
    Atualiza parâmetros e análise da estratégia quando ela muda
    """
    try:
        if strategy == 'iron_condor':
            expiry = datetime.now() + timedelta(days=30)
            positions = await strategy_service.iron_condor("BTC/USD", expiry)
            metrics = await strategy_service.calculate_strategy_metrics(positions)
            
            return (
                html.Div([
                    html.H5("Iron Condor Parameters"),
                    html.P(f"Width: {0.1}")
                ]),
                html.Div([
                    html.H5("Strategy Metrics"),
                    html.P(f"Total Cost: ${metrics['total_cost']:.2f}"),
                    html.P(f"Delta: {metrics['greeks']['delta']:.2f}"),
                    html.P(f"Gamma: {metrics['greeks']['gamma']:.2f}")
                ])
            )
        
        elif strategy == 'butterfly':
            expiry = datetime.now() + timedelta(days=30)
            positions = await strategy_service.butterfly("BTC/USD", expiry)
            metrics = await strategy_service.calculate_strategy_metrics(positions)
            
            return (
                html.Div([
                    html.H5("Butterfly Parameters"),
                    html.P(f"Width: {0.05}")
                ]),
                html.Div([
                    html.H5("Strategy Metrics"),
                    html.P(f"Total Cost: ${metrics['total_cost']:.2f}"),
                    html.P(f"Delta: {metrics['greeks']['delta']:.2f}"),
                    html.P(f"Gamma: {metrics['greeks']['gamma']:.2f}")
                ])
            )
            
        # Default case
        return html.Div("Selecione uma estratégia"), html.Div("")
            
    except Exception as e:
        print(f"Erro ao atualizar estratégia: {e}")
        return html.Div("Erro"), html.Div("Erro")

def run_server() -> None:
    """
    Inicia o servidor Dash
    """
    app.run_server(debug=True, port=8050)
