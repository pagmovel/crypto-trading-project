import asyncio
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any, Optional

from services.ccxt_service import CCXTService
from services.analysis_service import AnalysisService
from services.visualization_service import VisualizationService
from models.market_model import OptionContract, OptionAnalysis

class App:
    def __init__(self) -> None:
        self.ccxt_service = CCXTService()
        self.analysis_service = AnalysisService()
        self.visualization_service = VisualizationService()
        
    async def main(self) -> None:
        # Exemplo de uso do sistema
        symbol = "BTC/USD"
        expiry = datetime.now() + timedelta(days=30)
        
        try:
            # Busca dados de opções
            options_data = await self.ccxt_service.fetch_options_data(symbol, expiry)
            options: List[OptionContract] = []
            
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
                options.append(option)
            
            # Análise de opções
            analysis_results: Dict[str, OptionAnalysis] = {}
            for option in options:
                # Calcula volatilidade implícita
                spot_price = await self.ccxt_service.get_underlying_price(option.underlying)
                implied_vol = self.analysis_service.calculate_implied_volatility(
                    strike=option.strike_price,
                    spot=spot_price,
                    time_to_expiry=option.time_to_expiry,
                    is_call=option.is_call
                )
                
                # Calcula os Greeks
                greeks = self.analysis_service.calculate_greeks(
                    spot=spot_price,
                    strike=option.strike_price,
                    time_to_expiry=option.time_to_expiry,
                    volatility=implied_vol,
                    is_call=option.is_call
                )
                
                # Calcula valores intrínsecos e extrínsecos
                intrinsic = max(0, spot_price - option.strike_price) if option.is_call else max(0, option.strike_price - spot_price)
                extrinsic = option.current_price - intrinsic
                
                analysis_results[option.contract_id] = OptionAnalysis(
                    contract=option,
                    implied_volatility=implied_vol,
                    theoretical_price=option.current_price,
                    intrinsic_value=intrinsic,
                    extrinsic_value=extrinsic,
                    greeks={
                        'delta': greeks.delta,
                        'gamma': greeks.gamma,
                        'theta': greeks.theta,
                        'vega': greeks.vega,
                        'rho': greeks.rho
                    }
                )
            
            # Visualização
            self.visualization_service.plot_volatility_surface(options, analysis_results)
            self.visualization_service.plot_greeks_surface(options, analysis_results)
            
            # Exemplo de análise de uma opção específica
            if options:
                price_range = (options[0].strike_price * 0.5, options[0].strike_price * 1.5)
                self.visualization_service.plot_option_payoff(options[0], price_range, analysis_results)
            
        except Exception as e:
            print(f"Erro durante a execução: {e}")
        finally:
            await self.ccxt_service.close()

if __name__ == "__main__":
    app = App()
    asyncio.run(app.main())
