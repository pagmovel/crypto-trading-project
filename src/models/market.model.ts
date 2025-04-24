export class Market {
    symbol: string;
    price: number;
    volume: number;

    constructor(symbol: string, price: number, volume: number) {
        this.symbol = symbol;
        this.price = price;
        this.volume = volume;
    }
}

export interface OptionContract {
    symbol: string;
    type: 'call' | 'put';
    strike: number;
    expiry: Date;
    underlying: string;
    lastPrice?: number;
    volume?: number;
    openInterest?: number;
}

export interface Greeks {
    delta: number;
    gamma: number;
    theta: number;
    vega: number;
    rho?: number;
}

export interface OptionAnalysis extends OptionContract {
    greeks: Greeks;
    impliedVolatility: number;
    theoreticalPrice: number;
    extrinsicValue: number;
    intrinsicValue: number;
}

export interface MarketData {
    timestamp: Date;
    price: number;
    volume: number;
    high: number;
    low: number;
    open: number;
    close: number;
}

export interface Exchange {
    name: string;
    apiKey?: string;
    secret?: string;
    testnet?: boolean;
}