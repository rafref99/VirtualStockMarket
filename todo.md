# Todo

Most original app-level tasks are now implemented. Remaining work is release polish, deeper simulation, and richer gameplay.

## Recently Implemented

- Added a dashboard home tab with cash, holdings, debt, net worth, biggest movers, top news, active orders, and risk alerts.
- Added achievements for first trade, profit, diversification, borrowing, debt repayment, orders, news reading, and leaderboard rank.
- Added market sorting, key-action tooltips, clearer dashboard empty states, and a portfolio allocation chart.
- Finished the UI/UX todo pass with secondary-action tooltips, denser tab headers, news quality dashboard, and loan due-date dashboard.
- Added scrollable Settings with credits.
- Added category-specific market price ceilings and save-file price normalization.
- Added 50 more achievement milestones.
- Completed the Bank And Risk pass with credit limits, minimum payments, due dates, late/default penalties, margin trading, short selling, liquidation risk, credit scores, and insurance hedges.
- Added graphical pulse/confetti effects and optional sound cues for trades, orders, achievements, risk events, and manual ticks.

## Gameplay

- Add daily quests and challenge modes.
- Add trading goals with rewards.
- Add company profiles with financials, risk rating, sector outlook, and earnings reports.
- Add dividends with ex-dividend dates instead of random payouts.
- Add IPOs, delistings, bankruptcies, mergers, and stock splits.
- Add difficulty presets with different starting cash, volatility, and loan limits.

## Market Simulation

- Make news impact more realistic by linking each story to sectors, assets, duration, delayed reversals, and confidence.
- Add inflation, interest rates, unemployment, oil price, and currency indexes.
- Add sector cycles so tech, energy, finance, crypto, FNTs, commodities, and funds behave differently.
- Add market hours or weekend behavior for realistic mode.
- Add smarter offline simulation that compresses long absences without generating excessive ticks.

## News

- Add source reputation history so users can learn which sources are reliable.
- Add article bookmarks.
- Add read/unread state.
- Add news search.
- Add an impact timeline showing whether a news prediction helped or misled.
- Add breaking-news alerts for high-impact events.
- Add richer generated article images or reusable image assets.
- Expand market event headline translations beyond the core UI labels.

## Data And Quality

- Add import/export save files.
- Add reset-market and reset-account options.
- Add automated tests for trading, loans, orders, news, and offline simulation.
- Add a small migration system for old `data/*.json` files.
- Continue moving large UI sections into smaller view classes if the interface grows further.

## Release Polish

- Test the Windows launcher on a real Windows machine.
- Package platform-specific executables with PyInstaller.
- Add screenshots to the README.
