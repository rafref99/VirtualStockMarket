# Virtual Stock Market

A local Python desktop simulation of a lively fake-currency stock market. Users register or log in, receive 100 fake currency units, browse a generated market, buy and sell assets, and watch price history update on charts.

## Run

Double-click `run_app.command` on macOS, or run the app directly:

```bash
python3 app.py
```

The app uses only the Python standard library. It was built for Python 3.12, but should work on modern Python 3 versions that include Tkinter.

The launcher checks that Python 3 and Tkinter are available. If future packages are added to `requirements.txt`, it installs them before opening the app.

## Data Storage

Runtime data is created inside the project directory:

- `data/users.json` stores usernames, salted password hashes, cash balances, portfolios, and recent transactions.
- `data/market.json` stores generated assets, current prices, sectors, history, volatility, trend, news, and recent events.

Passwords are not stored as plain text. The app stores PBKDF2-SHA256 hashes with per-user salts.

## Gameplay

- Register or log in from the opening screen.
- Use `Remember me` to prefill the last username on the next launch. Passwords are never remembered.
- New users start with `100 FC`.
- Browse stocks, crypto, FNTs, commodities, and funds.
- See green and red market-list change indicators for rising and falling assets.
- Buy and sell decimal quantities based on your available fake cash and holdings.
- Watch the selected asset's chart update as the simulated market moves.
- Switch each asset chart between `Hours`, `Days`, `Week`, `Years`, and `Max` views.
- Click the chart to inspect the nearest price point with a visual marker and tooltip.
- Double-click a portfolio holding to switch the graph to that asset.
- Use the Settings tab for account details, system info, dark mode, and language selection.
- Switch UI language between English, German, Russian, Greek, Spanish, and Arabic.
- Use the branded sidebar logo and icon-labeled controls for faster navigation.
- React to richer events like earnings surprises, product launches, lawsuits, analyst changes, crypto security scares, supply shocks, fund inflows, and market-wide rotations.
- Freeze and resume live market updates.
- Set a custom live market step speed in seconds.
- Press `Simulate Next Market Tick` to advance the market manually.

## Project Layout

```text
.
├── app.py
├── config.py
├── i18n.py
├── market.py
├── storage.py
├── ui.py
├── README.md
├── features.md
├── todo.md
├── requirements.txt
├── run_app.command
└── data/
```

`data/` is created automatically when the app first runs.

## Code Organization

- `app.py` is the small application entry point.
- `ui.py` contains the Tkinter screens and interaction logic.
- `market.py` contains asset generation, price movement, and event simulation.
- `storage.py` contains JSON persistence, password hashing, and session data.
- `i18n.py` contains translations and theme color definitions.
- `config.py` contains shared paths, chart ranges, and formatting helpers.

## Resetting The Simulation

To start over, close the app and delete the generated `data/` directory. The next run will recreate a fresh market and empty user database.
