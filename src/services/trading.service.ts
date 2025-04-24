// src/services/trading.service.ts

import { CCXTService } from './ccxt.service';
import { AnalysisService } from './analysis.service';
import { OptionContract, Greeks, OptionAnalysis } from '../models/market.model';
import { settings } from '../config/settings';

export class TradingService {
    private ccxtService: CCXTService;
    private analysisService: AnalysisService;

    constructor(exchangeId: string, apiKey?: string, secret?: string) {
        this.ccxtService = new CCXTService(exchangeId, apiKey, secret);
        this.analysisService = new AnalysisService();
    }

    async analyzeOption(contract: OptionContract, spotPrice: number): Promise<OptionAnalysis> {
        const timeToExpiry = this.calculateTimeToExpiry(contract.expiry);
        
        // Calcula preço teórico e Greeks
        const theoreticalPrice = this.analysisService.calculateOptionPrice(
            spotPrice,
            contract.strike,
            timeToExpiry,
            settings.riskFreeRate,
            0.5, // Volatilidade inicial estimada
            contract.type
        );

        const greeks: Greeks = {
            delta: this.analysisService.calculateDelta(
                spotPrice,
                contract.strike,
                timeToExpiry,
                settings.riskFreeRate,
                0.5,
                contract.type
            ),
            gamma: this.analysisService.calculateGamma(
                spotPrice,
                contract.strike,
                timeToExpiry,
                settings.riskFreeRate,
                0.5
            ),
            theta: this.analysisService.calculateTheta(
                spotPrice,
                contract.strike,
                timeToExpiry,
                settings.riskFreeRate,
                0.5,
                contract.type
            ),
            vega: this.analysisService.calculateVega(
                spotPrice,
                contract.strike,
                timeToExpiry,
                settings.riskFreeRate,
                0.5
            )
        };

        // Calcula valor intrínseco e extrínseco
        const intrinsicValue = this.calculateIntrinsicValue(
            contract.type,
            spotPrice,
            contract.strike
        );

        return {
            ...contract,
            greeks,
            theoreticalPrice,
            impliedVolatility: 0.5, // Implementar cálculo de IV
            extrinsicValue: theoreticalPrice - intrinsicValue,
            intrinsicValue
        };
    }

    private calculateTimeToExpiry(expiry: Date): number {
        const now = new Date();
        const diff = expiry.getTime() - now.getTime();
        return diff / (1000 * 60 * 60 * 24 * settings.daysInYear);
    }

    private calculateIntrinsicValue(
        type: 'call' | 'put',
        spot: number,
        strike: number
    ): number {
        if (type === 'call') {
            return Math.max(0, spot - strike);
        } else {
            return Math.max(0, strike - spot);
        }
    }

    async monitorOption(contract: OptionContract, interval: number = settings.updateInterval): Promise<void> {
        setInterval(async () => {
            try {
                const spotPrice = await this.ccxtService.getOptionPrice(contract.underlying);
                const analysis = await this.analyzeOption(contract, spotPrice);
                console.log(`Análise atualizada para ${contract.symbol}:`, analysis);
            } catch (error) {
                console.error('Erro ao monitorar opção:', error);
            }
        }, interval);
    }
}