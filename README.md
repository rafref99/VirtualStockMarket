# Virtual Stock Market

**Virtual Stock Market** is a local Python desktop app that simulates a living fake-currency market. Create an account, start with `100 FC`, trade stocks/crypto/FNTs/commodities/funds, watch charts move in real time, react to market events, and compete on a local leaderboard.

No real money. No external market API. Just a self-contained trading sandbox built with Python and Tkinter.

## Fast Start

### macOS

Double-click:

```text
run_app.command
```

### Windows

Double-click:

```text
run_app_windows.bat
```

### Manual Run

```bash
python3 app.py
```

On Windows, use either:

```bat
py -3 app.py
```

or:

```bat
python app.py
```

## Requirements

- Python 3.10 or newer recommended.
- Tkinter must be available. It is included with most standard Python installs.
- No third-party packages are currently required.

The launcher scripts check Python, Tkinter, and `requirements.txt` before starting the app. If dependencies are added later, the launchers will install them automatically.

## Highlights

- Local login/register flow with salted password hashing.
- New users start with `100 FC` fake currency.
- Remember-me option that stores only the last username, never the password.
- 110 generated assets, including Bitcoin, Microsoft, Apple, Alphabet, Amazon, Tesla, Nvidia, Ethereum, and Meta.
- Stocks, crypto, FNTs, commodities, and funds.
- Live market updates with freeze/resume and adjustable tick speed.
- Manual market tick button for testing or slower play.
- Clickable charts with price tooltips and point markers.
- Chart ranges: `Hours`, `Days`, `Week`, `Years`, and `Max`.
- Green/red market movement indicators.
- Buy, sell, limit buy, limit sell, and stop-loss orders.
- Portfolio value tracking and performance chart.
- Transaction history, active orders, news feed, and local leaderboard tabs.
- Complex market events: earnings surprises, lawsuits, product launches, crypto scares, supply shocks, fund flows, and broad market rotations.
- Occasional dividends for held stocks and funds.
- Settings for dark mode, language, simulation speed, volatility, and event frequency.
- UI translations for English, German, Russian, Greek, Spanish, and Arabic.
- Keyboard shortcuts for common trading actions.

## First Run

1. Open the app with one of the launcher scripts or `python3 app.py`.
2. Register a new account.
3. Start with `100 FC`.
4. Select an asset in the Market tab.
5. Buy, sell, place orders, or watch the chart update live.
6. Use the Settings tab to enable dark mode, change language, or tune the simulation.

## Keyboard Shortcuts

| Shortcut | Action |
| --- | --- |
| `Ctrl+B` | Buy selected asset |
| `Ctrl+S` | Sell selected asset |
| `Ctrl+R` | Refresh |
| `Ctrl+L` | Logout |
| `Space` | Freeze/resume market updates |

## Data And Security

Runtime data is stored locally inside `data/`, which is ignored by git:

- `data/users.json`: users, salted password hashes, cash, portfolios, orders, transactions, and settings.
- `data/market.json`: generated assets, prices, history, sectors, news, simulation settings, and event state.
- `data/app_settings.json`: app-level preferences such as remembered username.

Passwords are not stored as plain text. The app uses PBKDF2-SHA256 with per-user salts.

## Project Structure

```text
.
├── app.py                 # Small application entry point
├── config.py              # Shared paths, constants, chart ranges, formatting
├── i18n.py                # Translations and theme color definitions
├── market.py              # Asset generation, price movement, market events
├── storage.py             # JSON persistence, account records, password hashing
├── ui.py                  # Tkinter UI, screens, tabs, interactions
├── run_app.command        # macOS double-click launcher
├── run_app_windows.bat    # Windows double-click launcher
├── requirements.txt       # Dependency list, currently empty
├── features.md            # Feature list and future ideas
├── todo.md                # Remaining roadmap/backlog
└── LICENSE                # MIT License
```

`data/` is created automatically on first launch.

## Development

Run a syntax check:

```bash
python3 -m py_compile app.py config.py i18n.py market.py storage.py ui.py
```

Run a quick market smoke test:

```bash
python3 -B -c "import market; m={'assets': market.generate_market()}; market.advance_market(m, 3); print(len(m['assets']))"
```

## Packaging

To build a standalone executable, use PyInstaller from a clean environment:

```bash
python3 -m pip install pyinstaller
python3 -m PyInstaller --onefile --windowed app.py
```

On Windows, use `py -3` or `python` instead of `python3`.

## Resetting The Simulation

Close the app and delete the generated `data/` directory. The next launch recreates a fresh market and empty user database.

## License

MIT License. See [LICENSE](LICENSE).
