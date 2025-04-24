import asyncio
import logging
from datetime import datetime, timedelta
import platform
from typing import List, Dict, Any, Optional

from services.ccxt_service import CCXTService
from services.analysis_service import AnalysisService
from services.visualization_service import VisualizationService
from models.market_model import OptionContract, OptionAnalysis

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class App:
    def __init__(self, simulation_mode: bool = True) -> None:
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
        self.ccxt_service = CCXTService(simulation_mode=simulation_mode)
        self.analysis_service = AnalysisService()
        self.visualization_service = VisualizationService()
        
    async def main(self) -> None:
        try:
            logger.info("Iniciando aplicação...")
            # Exemplo de uso do sistema
            symbol = "BTC/USD"
            expiry = datetime.now() + timedelta(days=30)
            
            logger.info(f"Buscando dados de opções para {symbol}")
            options_data = await self.ccxt_service.fetch_options_data(symbol, expiry)
            
            if not options_data:
                logger.warning("Nenhum dado de opção encontrado")
                return
                
            logger.info(f"Processando {len(options_data)} opções")
            options = []
            
            for data in options_data:
                try:
                    option = OptionContract(
                        symbol=data["symbol"],
                        strike_price=float(data["strike"]),
                        expiry=datetime.fromtimestamp(data["expiry"]),
                        contract_id=data["symbol"],
                        underlying=data["underlying"],
                        is_call=data["type"].upper() == "CALL",
                        current_price=float(data["price"])
                    )
                    options.append(option)
                    logger.info(f"Opção processada: {option.symbol}")
                except Exception as e:
                    logger.error(f"Erro ao processar opção: {e}")
                    continue
            
            logger.info("Realizando análise das opções")
            analysis_results: Dict[str, OptionAnalysis] = {}
            for option in options:
                try:
                    spot_price = await self.ccxt_service.get_underlying_price(option.underlying)
                    logger.info(f"Preço spot para {option.underlying}: {spot_price}")
                    
                    implied_vol = self.analysis_service.calculate_implied_volatility(
                        strike=option.strike_price,
                        spot=spot_price,
                        time_to_expiry=option.time_to_expiry,
                        is_call=option.is_call
                    )
                    logger.info(f"Volatilidade implícita calculada: {implied_vol:.2%}")
                    
                    greeks = self.analysis_service.calculate_greeks(
                        spot=spot_price,
                        strike=option.strike_price,
                        time_to_expiry=option.time_to_expiry,
                        volatility=implied_vol,
                        is_call=option.is_call
                    )
                    logger.info(f"Greeks calculados - Delta: {greeks.delta:.3f}, Gamma: {greeks.gamma:.3f}")
                    
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
                    logger.info(f"Análise completa para {option.symbol}")
                except Exception as e:
                    logger.error(f"Erro na análise da opção {option.contract_id}: {e}")
                    continue
            
            if analysis_results:
                logger.info("Gerando visualizações")
                self.visualization_service.plot_volatility_surface(options, analysis_results)
                self.visualization_service.plot_greeks_surface(options, analysis_results)
                
                if options:
                    price_range = (options[0].strike_price * 0.5, options[0].strike_price * 1.5)
                    self.visualization_service.plot_option_payoff(options[0], price_range, analysis_results)
            else:
                logger.warning("Nenhum resultado de análise disponível para visualização")
                
        except Exception as e:
            logger.error(f"Erro durante a execução: {e}", exc_info=True)
        finally:
            logger.info("Finalizando aplicação")
            await self.ccxt_service.close()

if __name__ == "__main__":
    app = App(simulation_mode=True)
    asyncio.run(app.main())
