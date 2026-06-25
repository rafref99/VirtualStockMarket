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
- Added graphical pulse/confetti effects for trades, orders, achievements, risk events, and manual ticks.
- Simplified the Bank tab with quick funding, next-due repayment, and optional advanced controls.
- Preserved selected market, news, portfolio, bank, and order items across live refreshes.
- Added news search, read/unread filtering, and article bookmarks.
- Added full save import/export plus reset-market and reset-account controls in Settings.
- Added macro indexes, sector cycles, company financial profiles, scheduled dividends, news impact outcomes, daily quests with rewards, and compressed offline simulation.
- Finished the News pass with source reputation history, breaking-news alerts, richer article images, and translated generated headlines.

## Gameplay

- Add challenge modes.
- Add trading goals with rewards.
- Add IPOs, delistings, bankruptcies, mergers, and stock splits.
- Add difficulty presets with different starting cash, volatility, and loan limits.

## Market Simulation

- Add market hours or weekend behavior for realistic mode.

## Data And Quality

- Add automated tests for trading, loans, orders, news, and offline simulation.
- Add a small migration system for old `data/*.json` files.
- Continue moving large UI sections into smaller view classes if the interface grows further.

## Release Polish

- Test the Windows launcher on a real Windows machine.
- Package platform-specific executables with PyInstaller.
- Add screenshots to the README.
