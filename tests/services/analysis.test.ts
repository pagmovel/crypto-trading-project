import { AnalysisService } from '../../src/services/analysis.service';

describe('AnalysisService', () => {
    let analysisService: AnalysisService;

    beforeEach(() => {
        analysisService = new AnalysisService();
    });

    test('should calculate moving average correctly', () => {
        const prices = [1, 2, 3, 4, 5];
        const period = 3;
        const result = analysisService.calculateMovingAverage(prices, period);
        expect(result).toEqual(4); // Expected moving average for the last 3 prices
    });

    test('should generate trading signals based on analysis', () => {
        const marketData = [
            { price: 100, volume: 10 },
            { price: 105, volume: 15 },
            { price: 102, volume: 20 },
        ];
        const signals = analysisService.generateTradingSignals(marketData);
        expect(signals).toContainEqual(expect.objectContaining({ signal: 'buy' }));
    });

    // Add more tests as needed
});