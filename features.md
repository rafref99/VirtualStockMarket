# Features

## Implemented

- Login and registration screen at app launch.
- Remember-me checkbox that saves only the last username locally.
- Local credential storage in `data/users.json`.
- Salted password hashing with PBKDF2-SHA256.
- Branded app logo in the sidebar.
- Icon-labeled primary controls.
- Double-click launch scripts for macOS and Windows.
- Starting balance of 100 fake currency units for every new user.
- Generated market with well-known assets including Bitcoin, Microsoft, Apple, Alphabet, Amazon, Tesla, Nvidia, Ethereum, and Meta.
- 100 additional random companies/assets across stocks, crypto, FNTs, commodities, and funds.
- Market browsing with category filters.
- Green and red market-list change indicators for rising and falling assets.
- Buy and sell support with decimal quantities.
- Limit buy, limit sell, and stop-loss orders.
- Occasional dividend payouts for held stocks and funds.
- Portfolio view with current holding values.
- Double-click portfolio holdings to select that asset in the market graph.
- Transaction history tab.
- Portfolio performance chart.
- News feed tab with filtering.
- Local leaderboard.
- Account summary with cash, holdings value, and net worth.
- Account management for password changes and account deletion.
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
- Simulation settings for speed presets, volatility, and event frequency.
- Keyboard shortcuts for buy, sell, refresh, logout, and freeze/resume.
- Guided first-run tutorial.
- Safer JSON normalization for older or manually edited save files.
- Local JSON persistence for users, holdings, transactions, and market state.
- Split module structure for easier maintenance: entry point, UI, market logic, storage, translations/themes, and config.

## Suggested Future Features

- Daily quests or challenges.
- Deeper company profiles and generated earnings statements.
- Import/export save files.
- Optional sound and visual effects for major market events.
