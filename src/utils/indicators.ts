// src/utils/indicators.ts

export function movingAverage(data: number[], period: number): number[] {
    const result: number[] = [];
    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) {
            result.push(null); // Not enough data to calculate the moving average
        } else {
            const avg = data.slice(i - period + 1, i + 1).reduce((sum, value) => sum + value, 0) / period;
            result.push(avg);
        }
    }
    return result;
}

export function calculateRSI(data: number[], period: number): number[] {
    const result: number[] = [];
    for (let i = 0; i < data.length; i++) {
        if (i < period) {
            result.push(null); // Not enough data to calculate RSI
        } else {
            const gains = [];
            const losses = [];
            for (let j = i - period + 1; j <= i; j++) {
                const change = data[j] - data[j - 1];
                if (change > 0) {
                    gains.push(change);
                } else {
                    losses.push(-change);
                }
            }
            const averageGain = gains.reduce((sum, value) => sum + value, 0) / period;
            const averageLoss = losses.reduce((sum, value) => sum + value, 0) / period;
            const rs = averageGain / averageLoss;
            const rsi = 100 - (100 / (1 + rs));
            result.push(rsi);
        }
    }
    return result;
}