import plotly from 'plotly';
import { OptionAnalysis, Greeks } from '../models/market.model';

export class VisualizationService {
    constructor() {}

    async plotVolatilitySurface(
        volatilitySurface: Array<{strike: number, expiry: Date, iv: number}>
    ): Promise<void> {
        const strikes = [...new Set(volatilitySurface.map(p => p.strike))];
        const expiries = [...new Set(volatilitySurface.map(p => p.expiry.getTime()))];
        
        const z = Array(strikes.length).fill(0).map(() => Array(expiries.length).fill(0));
        
        volatilitySurface.forEach(point => {
            const i = strikes.indexOf(point.strike);
            const j = expiries.indexOf(point.expiry.getTime());
            z[i][j] = point.iv;
        });

        const data = [{
            type: 'surface',
            x: expiries.map(t => new Date(t).toLocaleDateString()),
            y: strikes,
            z: z,
            colorscale: 'Viridis'
        }];

        const layout = {
            title: 'Superfície de Volatilidade',
            scene: {
                xaxis: { title: 'Vencimento' },
                yaxis: { title: 'Strike' },
                zaxis: { title: 'Volatilidade Implícita' }
            }
        };

        await plotly.plot(data, layout);
    }

    async plotGreeksProfile(
        analysis: OptionAnalysis,
        priceRange: [number, number],
        steps: number = 50
    ): Promise<void> {
        const prices = Array.from({ length: steps }, (_, i) => 
            priceRange[0] + (priceRange[1] - priceRange[0]) * i / (steps - 1)
        );

        const greeks = prices.map(price => ({
            price,
            delta: analysis.greeks.delta,
            gamma: analysis.greeks.gamma,
            theta: analysis.greeks.theta,
            vega: analysis.greeks.vega
        }));

        const data = [
            {
                x: prices,
                y: greeks.map(g => g.delta),
                name: 'Delta',
                type: 'scatter'
            },
            {
                x: prices,
                y: greeks.map(g => g.gamma),
                name: 'Gamma',
                type: 'scatter'
            },
            {
                x: prices,
                y: greeks.map(g => g.theta),
                name: 'Theta',
                type: 'scatter'
            },
            {
                x: prices,
                y: greeks.map(g => g.vega),
                name: 'Vega',
                type: 'scatter'
            }
        ];

        const layout = {
            title: 'Perfil dos Greeks',
            xaxis: { title: 'Preço do Ativo' },
            yaxis: { title: 'Valor' }
        };

        await plotly.plot(data, layout);
    }

    async plotOptionPayoff(
        analysis: OptionAnalysis,
        priceRange: [number, number],
        steps: number = 50
    ): Promise<void> {
        const prices = Array.from({ length: steps }, (_, i) => 
            priceRange[0] + (priceRange[1] - priceRange[0]) * i / (steps - 1)
        );

        const payoffs = prices.map(price => {
            const payoff = analysis.type === 'call'
                ? Math.max(0, price - analysis.strike)
                : Math.max(0, analysis.strike - price);
            return payoff - analysis.lastPrice;
        });

        const data = [{
            x: prices,
            y: payoffs,
            type: 'scatter',
            name: 'Payoff'
        }];

        const layout = {
            title: 'Perfil de Payoff da Opção',
            xaxis: { title: 'Preço do Ativo no Vencimento' },
            yaxis: { title: 'Lucro/Prejuízo' }
        };

        await plotly.plot(data, layout);
    }
}