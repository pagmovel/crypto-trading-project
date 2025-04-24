# crypto-trading-project

Este projeto é uma aplicação de negociação de criptomoedas que utiliza o módulo CCXT para interagir com várias exchanges. O objetivo é fornecer uma plataforma para análise de mercado e execução de operações de trading.

## Estrutura do Projeto

- `src/config/settings.ts`: Configurações da aplicação, incluindo chaves de API e variáveis de ambiente.
- `src/services/ccxt.service.ts`: Classe `CcxtService` para interagir com a biblioteca CCXT, incluindo métodos para buscar dados de mercado e executar trades.
- `src/services/analysis.service.ts`: Classe `AnalysisService` para analisar dados de mercado, calcular indicadores e gerar sinais de trading.
- `src/services/trading.service.ts`: Classe `TradingService` que gerencia operações de trading, incluindo colocação de ordens e gerenciamento de posições.
- `src/models/market.model.ts`: Classe `Market` que representa um mercado de trading, com propriedades como `symbol`, `price` e `volume`.
- `src/utils/indicators.ts`: Funções para calcular indicadores técnicos usados na análise de trading, como médias móveis e RSI.
- `src/utils/helpers.ts`: Funções utilitárias para tarefas comuns, como formatação de dados e logging.
- `src/app.ts`: Ponto de entrada da aplicação que inicializa os serviços e inicia a aplicação.

## Testes

Os testes estão localizados na pasta `tests/services` e incluem:

- `ccxt.test.ts`: Testes unitários para a classe `CcxtService`.
- `analysis.test.ts`: Testes unitários para a classe `AnalysisService`.

## Instalação

1. Clone o repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd crypto-trading-project
   ```

2. Instale as dependências:
   ```bash
   npm install
   ```

## Uso

Para iniciar a aplicação, execute:
```bash
npm start
```

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir um pull request ou relatar problemas.