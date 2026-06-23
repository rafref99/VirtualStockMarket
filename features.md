# Features

## Implemented

- Login and registration screen at app launch.
- Remember-me checkbox that saves only the last username locally.
- Local credential storage in `data/users.json`.
- Salted password hashing with PBKDF2-SHA256.
- Branded app logo in the sidebar.
- Icon-labeled primary controls.
- Starting balance of 100 fake currency units for every new user.
- Generated market with well-known assets including Bitcoin, Microsoft, Apple, Alphabet, Amazon, Tesla, Nvidia, Ethereum, and Meta.
- 100 additional random companies/assets across stocks, crypto, FNTs, commodities, and funds.
- Market browsing with category filters.
- Green and red market-list change indicators for rising and falling assets.
- Buy and sell support with decimal quantities.
- Portfolio view with current holding values.
- Double-click portfolio holdings to select that asset in the market graph.
- Account summary with cash, holdings value, and net worth.
- Price-history graph for the selected asset.
- Chart range selector with Hours, Days, Week, Years, and Max views.
- Clickable chart inspection with guide lines, highlighted point marker, and price tooltip.
- Market tick simulation with price movement, volatility, trends, and short news updates.
- Complex asset events including earnings beats/misses, product launches, lawsuits, analyst upgrades/downgrades, buyback rumors, crypto network events, FNT collector trends, commodity supply shocks, and fund inflows/outflows.
- Market-wide events that can affect a category, sector, or the whole market with temporary momentum and volatility changes.
- Recent event log for the selected asset.
- Live market updates with freeze/resume controls.
- Custom live market step speed, clamped between 0.5 and 60 seconds.
- Settings tab with account, appearance, language, and system sections.
- Dark mode toggle.
- UI language support for English, German, Russian, Greek, Spanish, and Arabic.
- Local JSON persistence for users, holdings, transactions, and market state.
- Split module structure for easier maintenance: entry point, UI, market logic, storage, translations/themes, and config.

## Suggested Future Features

- Leaderboards for multiple users on the same machine.
- Limit orders and stop-loss orders.
- Dividends for selected stocks and funds.
- Daily quests or challenges.
- Portfolio performance graph.
- Transaction history screen.
- Market sectors and richer company profiles.
- Import/export save files.
- Optional sound and visual effects for major market events.
