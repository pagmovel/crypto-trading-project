// src/config/settings.ts

export const settings = {
    // Configurações de Exchange
    defaultExchange: 'deribit',
    testnet: true,
    
    // Parâmetros do Modelo
    riskFreeRate: 0.05,  // 5% taxa livre de risco
    daysInYear: 365,
    
    // Intervalos de Atualização
    updateInterval: 60000, // 1 minuto em ms
    
    // Limites de Volatilidade
    minVolatility: 0.10,  // 10%
    maxVolatility: 2.00,  // 200%
    
    // Configurações de Trading
    maxPositionSize: 1.0,  // 100% do capital disponível
    stopLossPercent: 0.05, // 5% stop loss
    
    // URLs das APIs
    apiUrls: {
        mainnet: {
            deribit: 'https://www.deribit.com/api/v2',
            binance: 'https://api.binance.com/api/v3'
        },
        testnet: {
            deribit: 'https://test.deribit.com/api/v2',
            binance: 'https://testnet.binance.vision/api/v3'
        }
    }
};