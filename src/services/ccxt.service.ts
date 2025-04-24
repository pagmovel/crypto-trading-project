import ccxt from 'ccxt';
import { Exchange } from '../models/market.model';

export class CCXTService {
    private exchange: ccxt.Exchange;

    constructor(exchangeId: string, apiKey?: string, secret?: string) {
        this.exchange = new ccxt[exchangeId]({
            apiKey,
            secret,
            enableRateLimit: true
        });
    }

    async getOptionMarkets(symbol: string): Promise<any> {
        try {
            const markets = await this.exchange.fetchMarkets();
            return markets.filter(market => 
                market.type === 'option' && 
                market.base === symbol
            );
        } catch (error) {
            console.error('Erro ao buscar mercados de opções:', error);
            throw error;
        }
    }

    async getOptionPrice(symbol: string): Promise<number> {
        try {
            const ticker = await this.exchange.fetchTicker(symbol);
            return ticker.last;
        } catch (error) {
            console.error('Erro ao buscar preço da opção:', error);
            throw error;
        }
    }
}