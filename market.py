from __future__ import annotations

import math
import random
import string
import time

MAX_HISTORY = 1000
SECTORS = {
    "Stock": ["Technology", "Energy", "Finance", "Healthcare", "Consumer", "Industrial"],
    "Crypto": ["Digital Assets"],
    "FNT": ["Collectibles"],
    "Commodity": ["Commodities"],
    "Fund": ["Index Fund"],
}
MARKET_EVENT_CHANCE = 0.08
ASSET_EVENT_CHANCE = 0.025

def asset(symbol: str, name: str, category: str, price: float, volatility: float, trend: float, sector: str | None = None) -> dict:
    return {
        "symbol": symbol,
        "name": name,
        "category": category,
        "sector": sector or random.choice(SECTORS.get(category, ["General"])),
        "price": round(price, 2),
        "volatility": volatility,
        "trend": trend,
        "history": [round(price, 2)],
        "news": "Fresh listing",
        "event_log": [],
        "event_cooldown": 0,
        "event_momentum": 0.0,
        "event_momentum_ticks": 0,
    }


def generate_symbol(name: str, used: set[str]) -> str:
    base = "".join(ch for ch in name.upper() if ch in string.ascii_uppercase)[:4] or "CMP"
    symbol = base
    counter = 1
    while symbol in used:
        symbol = f"{base[:3]}{counter}"
        counter += 1
    used.add(symbol)
    return symbol


def generate_market() -> list[dict]:
    used: set[str] = set()
    known = [
        asset("BTC", "Bitcoin", "Crypto", 52.0, 0.065, 0.004, "Digital Assets"),
        asset("MSFT", "Microsoft", "Stock", 34.0, 0.025, 0.002, "Technology"),
        asset("AAPL", "Apple", "Stock", 31.5, 0.026, 0.0015, "Technology"),
        asset("GOOGL", "Alphabet", "Stock", 29.0, 0.028, 0.002, "Technology"),
        asset("AMZN", "Amazon", "Stock", 27.5, 0.032, 0.001, "Consumer"),
        asset("TSLA", "Tesla", "Stock", 23.0, 0.055, 0.001, "Industrial"),
        asset("NVDA", "Nvidia", "Stock", 38.0, 0.045, 0.003, "Technology"),
        asset("ETH", "Ethereum", "Crypto", 39.0, 0.06, 0.003, "Digital Assets"),
        asset("META", "Meta", "Stock", 25.0, 0.035, 0.001, "Technology"),
        asset("SPRK", "Spark Ape #42", "FNT", 14.0, 0.08, 0.0, "Collectibles"),
    ]
    for item in known:
        used.add(item["symbol"])

    prefixes = [
        "Nova", "Quantum", "Blue", "Solar", "Apex", "Vertex", "Lunar", "Nimbus", "Atlas", "Ever",
        "Copper", "Pixel", "Fusion", "Harbor", "Pulse", "Iron", "Cedar", "Orion", "Summit", "Civic",
    ]
    suffixes = [
        "Labs", "Energy", "Foods", "Robotics", "Bank", "Cloud", "Motors", "Media", "Health",
        "Mining", "Logistics", "Studios", "Security", "Textiles", "Aerospace", "Biotech",
    ]
    categories = ["Stock", "Crypto", "FNT", "Commodity", "Fund"]
    generated = []
    random.seed(42)
    while len(generated) < 100:
        name = f"{random.choice(prefixes)} {random.choice(suffixes)}"
        symbol = generate_symbol(name, used)
        category = random.choices(categories, weights=[58, 10, 10, 12, 10], k=1)[0]
        price = random.uniform(2.0, 48.0)
        volatility = random.uniform(0.012, 0.085 if category in {"Crypto", "FNT"} else 0.045)
        trend = random.uniform(-0.003, 0.004)
        generated.append(asset(symbol, name, category, price, volatility, trend))
    return known + generated


def add_event(item: dict, message: str, momentum: float, duration: int, volatility_boost: float = 0.0) -> None:
    item["news"] = message
    item["event_momentum"] = momentum
    item["event_momentum_ticks"] = duration
    item["event_cooldown"] = max(item.get("event_cooldown", 0), random.randint(4, 10))
    item["temporary_volatility"] = max(item.get("temporary_volatility", 0.0), volatility_boost)
    log = item.setdefault("event_log", [])
    log.append({"time": time.strftime("%Y-%m-%d %H:%M:%S"), "message": message})
    del log[:-8]


def maybe_asset_event(item: dict) -> None:
    if item.get("event_cooldown", 0) > 0 or random.random() > ASSET_EVENT_CHANCE:
        return

    category = item.get("category", "Stock")
    symbol = item["symbol"]
    stock_events = [
        (f"{symbol} reports stronger earnings than expected", 0.035, 8, 0.006),
        (f"{symbol} misses revenue targets and cuts guidance", -0.045, 9, 0.009),
        (f"{symbol} launches a major new product line", 0.028, 7, 0.005),
        (f"{symbol} faces a surprise lawsuit from a competitor", -0.035, 7, 0.008),
        (f"{symbol} announces cost cuts and margin improvements", 0.018, 6, 0.004),
        (f"Analysts upgrade {symbol} after institutional buying", 0.022, 5, 0.004),
        (f"Analysts downgrade {symbol} over slowing demand", -0.024, 5, 0.005),
        (f"{symbol} hints at a buyback program", 0.02, 6, 0.003),
    ]
    crypto_events = [
        (f"{symbol} spikes after exchange inflows surge", 0.045, 6, 0.018),
        (f"{symbol} drops after wallet security fears spread", -0.06, 7, 0.022),
        (f"{symbol} gains after network usage reaches a record", 0.038, 6, 0.016),
        (f"{symbol} weakens after regulators question trading volume", -0.05, 7, 0.02),
    ]
    fnt_events = [
        (f"{symbol} collection trends after a celebrity purchase", 0.065, 5, 0.03),
        (f"{symbol} floor price falls after mint oversupply", -0.07, 6, 0.032),
        (f"{symbol} gains rarity score attention from collectors", 0.04, 5, 0.022),
    ]
    commodity_events = [
        (f"{symbol} jumps after supply chain disruption", 0.03, 7, 0.011),
        (f"{symbol} falls as inventories build faster than expected", -0.028, 7, 0.01),
        (f"{symbol} steadies after producers agree to output limits", 0.018, 6, 0.007),
    ]
    fund_events = [
        (f"{symbol} attracts inflows after broad market optimism", 0.014, 8, 0.003),
        (f"{symbol} sees outflows as traders reduce risk", -0.016, 8, 0.004),
        (f"{symbol} rebalances toward stronger sectors", 0.011, 6, 0.002),
    ]
    event_pool = {
        "Crypto": crypto_events,
        "FNT": fnt_events,
        "Commodity": commodity_events,
        "Fund": fund_events,
    }.get(category, stock_events)
    message, momentum, duration, volatility_boost = random.choice(event_pool)
    add_event(item, message, momentum, duration, volatility_boost)


def maybe_market_event(market: dict) -> None:
    if random.random() > MARKET_EVENT_CHANCE:
        return

    assets = market.get("assets", [])
    if not assets:
        return
    target_type = random.choice(["category", "sector", "all"])
    if target_type == "category":
        target = random.choice(["Stock", "Crypto", "FNT", "Commodity", "Fund"])
        candidates = [item for item in assets if item.get("category") == target]
        label = target.lower()
    elif target_type == "sector":
        sectors = sorted({item.get("sector", "General") for item in assets})
        target = random.choice(sectors)
        candidates = [item for item in assets if item.get("sector", "General") == target]
        label = target.lower()
    else:
        target = "All"
        candidates = assets
        label = "the whole market"

    if not candidates:
        return

    market_events = [
        ("Central bank optimism lifts {label}", 0.012, 5, 0.004),
        ("Inflation worries pressure {label}", -0.014, 5, 0.006),
        ("Retail traders rotate into {label}", 0.018, 4, 0.008),
        ("Large funds reduce exposure to {label}", -0.02, 5, 0.009),
        ("Unexpected economic data shakes {label}", random.choice([-0.018, 0.018]), 4, 0.012),
        ("Liquidity improves across {label}", 0.01, 5, 0.003),
    ]
    template, momentum, duration, volatility_boost = random.choice(market_events)
    message = template.format(label=label)
    market["latest_event"] = message
    for item in candidates:
        add_event(item, message, momentum * random.uniform(0.6, 1.25), duration, volatility_boost)


def advance_market(market: dict, ticks: int = 1) -> None:
    for _ in range(max(1, ticks)):
        maybe_market_event(market)
        for item in market["assets"]:
            item.setdefault("sector", random.choice(SECTORS.get(item.get("category", "Stock"), ["General"])))
            item["event_cooldown"] = max(0, item.get("event_cooldown", 0) - 1)
            maybe_asset_event(item)

            momentum = item.get("event_momentum", 0.0) if item.get("event_momentum_ticks", 0) > 0 else 0.0
            if item.get("event_momentum_ticks", 0) > 0:
                item["event_momentum_ticks"] -= 1
                item["event_momentum"] *= 0.82
            temp_volatility = item.get("temporary_volatility", 0.0)
            if temp_volatility:
                item["temporary_volatility"] = max(0.0, temp_volatility * 0.75)

            volatility = item.get("volatility", 0.03) + temp_volatility
            shock = random.gauss(item.get("trend", 0) + momentum, volatility)
            cycle = math.sin(time.time() / 40 + len(item["symbol"])) * 0.006
            new_price = max(0.25, item["price"] * (1 + shock + cycle))
            item["price"] = round(new_price, 2)
            history = item.setdefault("history", [])
            history.append(item["price"])
            del history[:-MAX_HISTORY]
            if abs(shock) > volatility * 1.4:
                direction = "rallies" if shock > 0 else "slides"
                item["news"] = f"{item['symbol']} {direction} after heavy trading"
    market["last_tick"] = time.time()

