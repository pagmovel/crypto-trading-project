import asyncio
import os
from datetime import datetime, timedelta
import sys
from pathlib import Path
from dotenv import load_dotenv

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.services.ccxt_service import CCXTService
from src.services.strategy_service import StrategyService
from src.services.risk_service import RiskService
from src.services.visualization_service import VisualizationService
from src.models.market_model import OptionContract


async def main():
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
        spot_price = await ccxt_service.get_underlying_price(
            "BTC-USD"
        )  # Corrigido aqui
        print(f"Preço atual do Bitcoin: ${spot_price:,.2f}")

        # Cria um portfólio de exemplo com diferentes estratégias
        expiry_30d = datetime.now() + timedelta(days=30)
        expiry_60d = datetime.now() + timedelta(days=60)

        # 1. Bull Call Spread
        bull_spread_options, _ = strategy_service.create_bull_spread(
            spot_price=spot_price,
            expiry=expiry_30d,
            lower_strike=spot_price * 0.95,
            upper_strike=spot_price * 1.05,
            underlying="BTC",
        )

        # 2. Iron Condor
        iron_condor_options, _ = strategy_service.create_iron_condor(
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

        # Analisa risco do portfólio
        risk_metrics = risk_service.calculate_portfolio_risk(
            positions=positions, spot_price=spot_price, confidence_level=0.95, days=1
        )

        print("\n=== Análise de Risco do Portfólio ===")
        print(f"VaR (95%, 1 dia): ${risk_metrics['var']:,.2f}")
        print(f"Expected Shortfall: ${risk_metrics['expected_shortfall']:,.2f}")

        print("\nGreeks do Portfólio:")
        print(f"Delta: {risk_metrics['greeks'].delta:.4f}")
        print(f"Gamma: {risk_metrics['greeks'].gamma:.4f}")
        print(f"Theta: {risk_metrics['greeks'].theta:.4f}")
        print(f"Vega: {risk_metrics['greeks'].vega:.4f}")

        print("\nResultados do Stress Test:")
        for scenario, value in risk_metrics["stress_test"].items():
            print(f"{scenario}: ${value:,.2f}")

        print("\nConcentração do Portfólio:")
        print("Por tipo:")
        for type_, conc in risk_metrics["position_concentration"]["by_type"].items():
            print(f"{type_}: {conc*100:.1f}%")

        print("\nPor vencimento:")
        for date, conc in risk_metrics["position_concentration"]["by_expiry"].items():
            print(f"{date}: {conc*100:.1f}%")

        # Otimiza portfólio
        print("\n=== Otimização de Portfólio ===")
        available_options = bull_spread_options + iron_condor_options

        optimized_positions = risk_service.optimize_portfolio(
            available_options=available_options,
            target_delta=0.2,  # Levemente direcional
            max_vega=1000,  # Limite exposição à volatilidade
            max_theta=-50,  # Limite decay diário
            budget=100000,  # Orçamento de $100k
            spot_price=spot_price,
        )

        print("\nPortfólio Otimizado:")
        for contract, quantity in optimized_positions:
            print(f"{contract.symbol}: {quantity} contratos")

        optimized_greeks = risk_service._calculate_portfolio_greeks(
            optimized_positions, spot_price
        )

        print("\nGreeks do Portfólio Otimizado:")
        print(f"Delta: {optimized_greeks.delta:.4f}")
        print(f"Gamma: {optimized_greeks.gamma:.4f}")
        print(f"Theta: {optimized_greeks.theta:.4f}")
        print(f"Vega: {optimized_greeks.vega:.4f}")

    except Exception as error:
        print(f"Erro na execução: {error}")


if __name__ == "__main__":
    asyncio.run(main())
