// src/services/analysis.service.ts

import { norm } from 'scipy';
import numpy as np;

export class AnalysisService {
    constructor() {
        // Initialize any necessary properties or dependencies
    }

    calculateMovingAverage(data: number[], period: number): number {
        if (data.length < period) {
            throw new Error("Data length is less than the period.");
        }
        const sum = data.slice(-period).reduce((acc, val) => acc + val, 0);
        return sum / period;
    }

    calculateRSI(data: number[], period: number): number {
        if (data.length < period) {
            throw new Error("Data length is less than the period.");
        }
        let gains = 0;
        let losses = 0;

        for (let i = 1; i < period; i++) {
            const difference = data[i] - data[i - 1];
            if (difference > 0) {
                gains += difference;
            } else {
                losses -= difference; // losses are negative
            }
        }

        const averageGain = gains / period;
        const averageLoss = losses / period;

        if (averageLoss === 0) {
            return 100; // Avoid division by zero
        }

        const rs = averageGain / averageLoss;
        return 100 - (100 / (1 + rs));
    }

    generateTradingSignal(data: number[], period: number): string {
        const movingAverage = this.calculateMovingAverage(data, period);
        const currentPrice = data[data.length - 1];

        if (currentPrice > movingAverage) {
            return "BUY";
        } else if (currentPrice < movingAverage) {
            return "SELL";
        } else {
            return "HOLD";
        }
    }

    // Cálculo do preço da opção usando Black-Scholes
    public calculateOptionPrice(
        spot: number,
        strike: number,
        timeToExpiry: number,
        riskFreeRate: number,
        volatility: number,
        optionType: 'call' | 'put'
    ): number {
        const d1 = this.calculateD1(spot, strike, timeToExpiry, riskFreeRate, volatility);
        const d2 = d1 - volatility * Math.sqrt(timeToExpiry);

        if (optionType === 'call') {
            return spot * this.normalCDF(d1) - strike * Math.exp(-riskFreeRate * timeToExpiry) * this.normalCDF(d2);
        } else {
            return strike * Math.exp(-riskFreeRate * timeToExpiry) * this.normalCDF(-d2) - spot * this.normalCDF(-d1);
        }
    }

    // Cálculo dos Greeks
    public calculateDelta(
        spot: number,
        strike: number,
        timeToExpiry: number,
        riskFreeRate: number,
        volatility: number,
        optionType: 'call' | 'put'
    ): number {
        const d1 = this.calculateD1(spot, strike, timeToExpiry, riskFreeRate, volatility);
        return optionType === 'call' ? this.normalCDF(d1) : this.normalCDF(d1) - 1;
    }

    public calculateGamma(
        spot: number,
        strike: number,
        timeToExpiry: number,
        riskFreeRate: number,
        volatility: number
    ): number {
        const d1 = this.calculateD1(spot, strike, timeToExpiry, riskFreeRate, volatility);
        return this.normalPDF(d1) / (spot * volatility * Math.sqrt(timeToExpiry));
    }

    public calculateTheta(
        spot: number,
        strike: number,
        timeToExpiry: number,
        riskFreeRate: number,
        volatility: number,
        optionType: 'call' | 'put'
    ): number {
        const d1 = this.calculateD1(spot, strike, timeToExpiry, riskFreeRate, volatility);
        const d2 = d1 - volatility * Math.sqrt(timeToExpiry);
        
        const term1 = -(spot * volatility * this.normalPDF(d1)) / (2 * Math.sqrt(timeToExpiry));
        
        if (optionType === 'call') {
            const term2 = -riskFreeRate * strike * Math.exp(-riskFreeRate * timeToExpiry) * this.normalCDF(d2);
            return term1 + term2;
        } else {
            const term2 = riskFreeRate * strike * Math.exp(-riskFreeRate * timeToExpiry) * this.normalCDF(-d2);
            return term1 + term2;
        }
    }

    public calculateVega(
        spot: number,
        strike: number,
        timeToExpiry: number,
        riskFreeRate: number,
        volatility: number
    ): number {
        const d1 = this.calculateD1(spot, strike, timeToExpiry, riskFreeRate, volatility);
        return spot * Math.sqrt(timeToExpiry) * this.normalPDF(d1);
    }

    public calculateImpliedVolatility(
        marketPrice: number,
        spot: number,
        strike: number,
        timeToExpiry: number,
        riskFreeRate: number,
        optionType: 'call' | 'put',
        tolerance: number = 0.0001,
        maxIterations: number = 100
    ): number {
        let sigma = 0.5;  // Volatilidade inicial
        let iteration = 0;
        
        while (iteration < maxIterations) {
            const price = this.calculateOptionPrice(
                spot,
                strike,
                timeToExpiry,
                riskFreeRate,
                sigma,
                optionType
            );
            
            const vega = this.calculateVega(
                spot,
                strike,
                timeToExpiry,
                riskFreeRate,
                sigma
            );
            
            const diff = price - marketPrice;
            
            if (Math.abs(diff) < tolerance) {
                return sigma;
            }
            
            // Newton-Raphson step
            sigma = sigma - diff / vega;
            
            // Limites de volatilidade
            sigma = Math.max(0.01, Math.min(sigma, 5));
            
            iteration++;
        }
        
        throw new Error('Implied volatility calculation did not converge');
    }

    public async calculateVolatilitySurface(
        options: OptionContract[],
        spotPrice: number,
        riskFreeRate: number
    ): Promise<Array<{strike: number, expiry: Date, iv: number}>> {
        return Promise.all(
            options.map(async (option) => {
                const timeToExpiry = this.calculateTimeToExpiry(option.expiry);
                const iv = this.calculateImpliedVolatility(
                    option.lastPrice || 0,
                    spotPrice,
                    option.strike,
                    timeToExpiry,
                    riskFreeRate,
                    option.type
                );
                
                return {
                    strike: option.strike,
                    expiry: option.expiry,
                    iv
                };
            })
        );
    }

    private calculateD1(
        spot: number,
        strike: number,
        timeToExpiry: number,
        riskFreeRate: number,
        volatility: number
    ): number {
        return (Math.log(spot / strike) + (riskFreeRate + volatility * volatility / 2) * timeToExpiry) / 
               (volatility * Math.sqrt(timeToExpiry));
    }

    private normalCDF(x: number): number {
        return (1.0 + Math.erf(x / Math.sqrt(2.0))) / 2.0;
    }

    private normalPDF(x: number): number {
        return Math.exp(-(x * x) / 2.0) / Math.sqrt(2.0 * Math.PI);
    }
}