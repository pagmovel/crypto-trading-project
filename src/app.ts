import { TradingService } from './services/trading.service';
import { settings } from './config/settings';
import { OptionContract } from './models/market.model';
import dotenv from 'dotenv';

// Carrega variáveis de ambiente
dotenv.config();

async function main() {
    try {
        // Inicializa serviço de trading
        const tradingService = new TradingService(
            settings.defaultExchange,
            process.env.API_KEY,
            process.env.API_SECRET
        );

        // Exemplo de contrato de opção para análise
        const optionContract: OptionContract = {
            symbol: 'BTC-31MAR23-50000-C',
            type: 'call',
            strike: 50000,
            expiry: new Date('2023-03-31'),
            underlying: 'BTC/USD'
        };

        // Inicia monitoramento da opção
        console.log('Iniciando monitoramento da opção:', optionContract.symbol);
        await tradingService.monitorOption(optionContract);

    } catch (error) {
        console.error('Erro na aplicação:', error);
    }
}

// Executa a aplicação
main().catch(console.error);