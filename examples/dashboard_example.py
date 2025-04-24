import asyncio
import os
from datetime import datetime, timedelta
import sys
from pathlib import Path
from dotenv import load_dotenv
import threading
import webbrowser
import time
import platform

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.services.ccxt_service import CCXTService
from src.services.strategy_service import StrategyService
from src.services.risk_service import RiskService
from src.web.app import app
from src.models.market_model import OptionContract


async def setup_strategy():
    try:
        # Carrega configurações
        load_dotenv()

        # Inicializa serviços
        ccxt_service = CCXTService(
            "deribit", api_key=os.getenv("API_KEY"), secret=os.getenv("API_SECRET")
        )
        strategy_service = StrategyService()
        risk_service = RiskService()

        # Busca preço atual do BTC
        spot_price = await ccxt_service.get_underlying_price("BTC-PERPETUAL")
        print(f"Preço atual do Bitcoin: ${spot_price:,.2f}")

        # Cria um portfólio de exemplo com diferentes estratégias
        expiry_30d = datetime.now() + timedelta(days=30)
        expiry_60d = datetime.now() + timedelta(days=60)

        # 1. Bull Call Spread
        bull_spread_options, bull_metrics = strategy_service.create_bull_spread(
            spot_price=spot_price,
            expiry=expiry_30d,
            lower_strike=round(spot_price * 0.95 / 100) * 100,
            upper_strike=round(spot_price * 1.05 / 100) * 100,
            underlying="BTC",
        )

        # 2. Iron Condor
        iron_condor_options, condor_metrics = strategy_service.create_iron_condor(
            spot_price=spot_price,
            expiry=expiry_60d,
            put_strikes=(spot_price * 0.85, spot_price * 0.90),
            call_strikes=(spot_price * 1.10, spot_price * 1.15),
            underlying="BTC",
        )

        # Combina as posições
        positions = [
            (bull_spread_options[0], 1),  # Long lower strike call
            (bull_spread_options[1], -1),  # Short upper strike call
            (iron_condor_options[0], 1),  # Long OTM put
            (iron_condor_options[1], -1),  # Short less OTM put
            (iron_condor_options[2], -1),  # Short less OTM call
            (iron_condor_options[3], 1),  # Long OTM call
        ]

        # Calcula métricas de risco
        risk_metrics = risk_service.calculate_portfolio_risk(
            positions=positions, spot_price=spot_price, confidence_level=0.95, days=1
        )

        # Atualiza variáveis globais do dashboard
        from src.web.app import positions as dash_positions
        from src.web.app import risk_metrics as dash_risk_metrics

        dash_positions.extend(
            [
                {
                    "name": "Bull Call Spread",
                    "strike": bull_spread_options[0].strike,
                    "calc_payoff": lambda x: max(0, x - bull_spread_options[0].strike)
                    - max(0, x - bull_spread_options[1].strike)
                    - bull_metrics["net_cost"],
                },
                {
                    "name": "Iron Condor",
                    "strike": iron_condor_options[0].strike,
                    "calc_payoff": lambda x: max(0, iron_condor_options[0].strike - x)
                    - max(0, iron_condor_options[1].strike - x)
                    - max(0, x - iron_condor_options[2].strike)
                    + max(0, x - iron_condor_options[3].strike)
                    + condor_metrics["net_credit"],
                },
            ]
        )

        # Configuração global do risk_metrics
        global risk_metrics
        risk_metrics = risk_metrics

        print("\nEstratégias configuradas com sucesso!")
        print("Dashboard disponível em http://localhost:8050")

    except Exception as error:
        print(f"Erro na execução: {error}")
    finally:
        if ccxt_service:
            await ccxt_service.close()


def open_browser():
    """Abre o navegador após 3 segundos"""
    time.sleep(3)
    webbrowser.open("http://localhost:8050")


if __name__ == "__main__":
    # Configura o loop de eventos apropriado para Windows
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Inicia thread para abrir o navegador
    threading.Thread(target=open_browser).start()

    # Configura estratégias
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_strategy())

    # Inicia o servidor Dash
    app.run(debug=False, host="0.0.0.0", port=8050)
