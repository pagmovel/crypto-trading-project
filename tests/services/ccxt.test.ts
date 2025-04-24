import { CcxtService } from '../../src/services/ccxt.service';

describe('CcxtService', () => {
    let ccxtService: CcxtService;

    beforeEach(() => {
        ccxtService = new CcxtService();
    });

    test('should fetch market data', async () => {
        const marketData = await ccxtService.fetchMarketData('BTC/USDT');
        expect(marketData).toHaveProperty('symbol', 'BTC/USDT');
        expect(marketData).toHaveProperty('price');
        expect(marketData).toHaveProperty('volume');
    });

    test('should execute a trade', async () => {
        const tradeResult = await ccxtService.executeTrade('BTC/USDT', 'buy', 1);
        expect(tradeResult).toHaveProperty('id');
        expect(tradeResult).toHaveProperty('symbol', 'BTC/USDT');
        expect(tradeResult).toHaveProperty('amount', 1);
    });
});