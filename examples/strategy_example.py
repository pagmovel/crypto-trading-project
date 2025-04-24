import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.services.ccxt_service import CCXTService
from src.services.strategy_service import StrategyService
from src.services.visualization_service import VisualizationService
from src.models.market_model import OptionAnalysis, OptionContract


async def main():
    ccxt_service = None
    try:
        # Carrega configurações
        load_dotenv()

        # Inicializa serviços
        ccxt_service = CCXTService(
            "deribit", api_key=os.getenv("API_KEY"), secret=os.getenv("API_SECRET")
        )
        strategy_service = StrategyService()
        viz_service = VisualizationService()

        # Busca preço atual do BTC usando o símbolo perpétuo
        spot_price = await ccxt_service.get_underlying_price("BTC-PERPETUAL")
        print(f"Preço atual do Bitcoin: ${spot_price:,.2f}")

        # Define parâmetros para as estratégias
        expiry = datetime.now() + timedelta(days=30)  # Vencimento em 30 dias

        # 1. Cria Bull Call Spread
        print("\n=== Bull Call Spread ===")
        lower_strike = (
            round(spot_price * 0.95 / 100) * 100
        )  # Arredonda para centena mais próxima
        upper_strike = round(spot_price * 1.05 / 100) * 100

        options, metrics = strategy_service.create_bull_spread(
            spot_price=spot_price,
            expiry=expiry,
            lower_strike=lower_strike,
            upper_strike=upper_strike,
            underlying="BTC",
        )

        print(f'Custo líquido: ${metrics["net_cost"]:,.2f}')
        print(f'Lucro máximo: ${metrics["max_profit"]:,.2f}')
        print(f'Perda máxima: ${metrics["max_loss"]:,.2f}')
        print(f'Ponto de equilíbrio: ${metrics["break_even"]:,.2f}')
        print("\nGreeks:")
        print(f'Delta: {metrics["greeks"].delta:.4f}')
        print(f'Gamma: {metrics["greeks"].gamma:.4f}')
        print(f'Theta: {metrics["greeks"].theta:.4f}')
        print(f'Vega: {metrics["greeks"].vega:.4f}')

        # Plota os gráficos para cada estratégia
        print("\nGerando visualizações...")

        await viz_service.plot_option_payoff(
            analysis=OptionAnalysis(
                contract=options[0],
                greeks=metrics["greeks"],
                implied_volatility=0.5,
                theoretical_price=metrics["net_cost"],
                extrinsic_value=metrics["net_cost"],
                intrinsic_value=0,
            ),
            price_range=(spot_price * 0.5, spot_price * 1.5),
        )

    except Exception as error:
        print(f"Erro na execução: {error}")
    finally:
        # Garante que a conexão seja fechada
        if ccxt_service:
            await ccxt_service.close()


if __name__ == "__main__":
    asyncio.run(main())
