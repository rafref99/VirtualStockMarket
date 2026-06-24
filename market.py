from __future__ import annotations

import math
import random
import string
import time

MAX_HISTORY = 1000
PRICE_LIMITS = {
    "Stock": 250_000.0,
    "Crypto": 500_000.0,
    "FNT": 100_000.0,
    "Commodity": 50_000.0,
    "Fund": 150_000.0,
}
SECTORS = {
    "Stock": ["Technology", "Energy", "Finance", "Healthcare", "Consumer", "Industrial"],
    "Crypto": ["Digital Assets"],
    "FNT": ["Collectibles"],
    "Commodity": ["Commodities"],
    "Fund": ["Index Fund"],
}
MARKET_EVENT_CHANCE = 0.08
ASSET_EVENT_CHANCE = 0.025
GLOBAL_STORY_CHANCE = 0.018
RARE_GLOBAL_STORY_CHANCE = 0.003
NEWS_TICK_COOLDOWN = 3
MAX_NEWS_PER_TICK = 1


def max_asset_price(item: dict) -> float:
    return PRICE_LIMITS.get(item.get("category", "Stock"), 250_000.0)


def clamp_asset_price(item: dict) -> None:
    cap = max_asset_price(item)
    item["price"] = round(min(max(float(item.get("price", 0.25)), 0.25), cap), 2)
    history = item.setdefault("history", [item["price"]])
    item["history"] = [round(min(max(float(price), 0.25), cap), 2) for price in history[-MAX_HISTORY:]]


def normalize_asset_prices(market: dict) -> None:
    for item in market.get("assets", []):
        if isinstance(item, dict):
            clamp_asset_price(item)


def source_profile(category: str, misleading: bool = False) -> dict:
    profiles = [
        ("Daily Ledger", "Newspaper", 0.78, "newspaper"),
        ("MarketWire", "Newswire", 0.72, "newspaper"),
        ("FinTube Alpha", "YouTuber", 0.42, "youtuber"),
        ("MacroScope", "Research Blog", 0.68, "newspaper"),
        ("Street Chatter", "Social Feed", 0.35, "youtuber"),
    ]
    if category == "Market":
        profiles.extend([
            ("Global Desk", "Newspaper", 0.82, "globe"),
            ("Frontier Briefing", "Science Desk", 0.74, "space"),
        ])
    if category == "Commodity":
        profiles.append(("Energy Sentinel", "Newspaper", 0.8, "oil"))
    if misleading:
        return {"name": "FinTube Alpha", "type": "YouTuber", "credibility": 0.28, "image_key": "youtuber"}
    name, source_type, credibility, image_key = random.choice(profiles)
    return {"name": name, "type": source_type, "credibility": credibility, "image_key": image_key}


def build_article(
    message: str,
    symbol: str,
    category: str,
    momentum: float = 0.0,
    duration: int = 0,
    source: dict | None = None,
    misleading: bool = False,
) -> dict:
    source = source or source_profile(category, misleading)
    direction = "bullish" if momentum > 0 else "bearish" if momentum < 0 else "mixed"
    topic = symbol if symbol != "MARKET" else category.lower()
    title_prefixes = {
        "Newspaper": ["Investors weigh", "Analysts study", "Market column:"],
        "Newswire": ["Breaking:", "Market update:", "Fast brief:"],
        "YouTuber": ["Influencer says invest in", "Viral clip pumps", "Creator shouts buy"],
        "Social Feed": ["Trending rumor:", "Retail traders debate", "Forum buzz:"],
        "Research Blog": ["Deep dive:", "Model update:", "Signal watch:"],
        "Science Desk": ["Frontier report:", "Space economy brief:", "Mission watch:"],
    }
    title_start = random.choice(title_prefixes.get(source["type"], ["Market brief:"]))
    title = f"{title_start} {topic} after new signal"
    if source["type"] == "YouTuber":
        title = f"{title_start} {topic}: \"this could explode\""
    if category == "Commodity":
        title = f"{title_start} {topic} as supply risks move prices"

    if misleading:
        insight = "Hype warning: the headline sounds confident, but the signal quality is weak and the move may reverse."
    elif momentum > 0:
        insight = f"Potential upside for {topic}; compare price momentum with order flow before buying."
    elif momentum < 0:
        insight = f"Risk signal for {topic}; defensive traders may wait or reduce exposure."
    else:
        insight = "Mixed signal; useful context, but not strong enough by itself."

    body = (
        f"{message}.\n\n"
        f"The article frames this as a {direction} signal lasting roughly {duration or 'several'} market tick(s). "
        f"Credibility is {source['credibility'] * 100:.0f}%, so the idea should be weighed against the chart and portfolio risk.\n\n"
        f"Investment insight: {insight}"
    )
    return {
        "title": title,
        "body": body,
        "source": source["name"],
        "source_type": source["type"],
        "credibility": source["credibility"],
        "impact": direction,
        "insight": insight,
        "misleading": misleading,
        "image_key": source["image_key"],
    }


def append_news(
    market: dict | None,
    message: str,
    symbol: str = "MARKET",
    category: str = "Market",
    momentum: float = 0.0,
    duration: int = 0,
    title: str | None = None,
    body: str | None = None,
    source: dict | None = None,
    image_key: str | None = None,
    misleading: bool = False,
    force: bool = False,
) -> None:
    if market is None:
        return
    if not force:
        cooldown = int(market.get("_news_cooldown_ticks", 0) or 0)
        created_this_tick = int(market.get("_news_created_this_tick", 0) or 0)
        if cooldown > 0 or created_this_tick >= MAX_NEWS_PER_TICK:
            return
    article = build_article(message, symbol, category, momentum, duration, source, misleading)
    if title:
        article["title"] = title
    if body:
        article["body"] = body
    if image_key:
        article["image_key"] = image_key
    feed = market.setdefault("news_feed", [])
    feed.append({
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "category": category,
        "message": message,
        **article,
    })
    del feed[:-180]
    if not force:
        market["_news_created_this_tick"] = int(market.get("_news_created_this_tick", 0) or 0) + 1
        market["_news_cooldown_ticks"] = NEWS_TICK_COOLDOWN

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


def seed_news(market: dict) -> None:
    if market.get("news_feed"):
        return
    assets = market.get("assets", [])
    if not assets:
        return
    tech = next((item for item in assets if item.get("sector") == "Technology"), assets[0])
    commodity = next((item for item in assets if item.get("category") == "Commodity"), assets[-1])
    crypto = next((item for item in assets if item.get("category") == "Crypto"), assets[0])
    append_news(
        market,
        f"{tech['symbol']} attracts analyst attention after product demand improves",
        tech["symbol"],
        tech.get("category", "Stock"),
        0.018,
        5,
        title=f"Newspaper watch: {tech['symbol']} demand story may support shares",
        body=(
            f"Daily Ledger says {tech['name']} is seeing stronger product demand and renewed investor attention.\n\n"
            "Investment insight: watch whether price confirms the story over the next few ticks before entering a large position."
        ),
        source={"name": "Daily Ledger", "type": "Newspaper", "credibility": 0.78, "image_key": "newspaper"},
        image_key="newspaper",
        force=True,
    )
    append_news(
        market,
        f"FinTube creator tells viewers to invest in {crypto['symbol']} before a rumored breakout",
        crypto["symbol"],
        crypto.get("category", "Crypto"),
        0.035,
        4,
        title=f"YouTuber says invest in {crypto['symbol']} before it rockets",
        body=(
            f"A viral creator claims {crypto['symbol']} is ready for a breakout. The clip is confident, but the argument relies mostly on attention and short-term momentum.\n\n"
            "Investment insight: this may be misleading. Hype can move price briefly and still become a bad entry."
        ),
        source={"name": "FinTube Alpha", "type": "YouTuber", "credibility": 0.31, "image_key": "youtuber"},
        image_key="youtuber",
        misleading=True,
        force=True,
    )
    append_news(
        market,
        f"{commodity['symbol']} traders monitor supply pressure after global shipping delays",
        commodity["symbol"],
        commodity.get("category", "Commodity"),
        0.022,
        6,
        title=f"Commodity desk: {commodity['symbol']} could react to supply pressure",
        body=(
            "Energy Sentinel reports that shipping delays are increasing attention on commodity supply chains.\n\n"
            "Investment insight: supply stories can lift commodity assets, but late entries after a spike carry reversal risk."
        ),
        source={"name": "Energy Sentinel", "type": "Newspaper", "credibility": 0.81, "image_key": "oil"},
        image_key="oil",
        force=True,
    )


def add_event(item: dict, message: str, momentum: float, duration: int, volatility_boost: float = 0.0, market: dict | None = None, misleading: bool = False) -> None:
    item["news"] = message
    item["event_momentum"] = momentum
    item["event_momentum_ticks"] = duration
    item["event_cooldown"] = max(item.get("event_cooldown", 0), random.randint(4, 10))
    item["temporary_volatility"] = max(item.get("temporary_volatility", 0.0), volatility_boost)
    log = item.setdefault("event_log", [])
    log.append({"time": time.strftime("%Y-%m-%d %H:%M:%S"), "message": message})
    del log[:-8]
    append_news(market, message, item.get("symbol", "MARKET"), item.get("category", "Market"), momentum, duration, misleading=misleading)


def maybe_asset_event(item: dict, market: dict, event_frequency: float) -> None:
    if item.get("event_cooldown", 0) > 0 or random.random() > ASSET_EVENT_CHANCE * event_frequency:
        return

    category = item.get("category", "Stock")
    symbol = item["symbol"]
    stock_events = [
        (f"{symbol} reports stronger earnings than expected", 0.035, 8, 0.006),
        (f"{symbol} misses revenue targets and cuts guidance", -0.045, 9, 0.009),
        (f"{symbol} launches a major new product line", 0.028, 7, 0.005),
        (f"{symbol} declares a special dividend for long-term holders", 0.018, 5, 0.003),
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
    add_event(item, message, momentum, duration, volatility_boost, market)


def maybe_market_event(market: dict, event_frequency: float) -> None:
    if random.random() > MARKET_EVENT_CHANCE * event_frequency:
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
    append_news(market, message, "MARKET", "Market", momentum, duration)
    for item in candidates:
        add_event(item, message, momentum * random.uniform(0.6, 1.25), duration, volatility_boost, market)


def apply_story_to_assets(market: dict, candidates: list[dict], message: str, momentum: float, duration: int, volatility_boost: float, misleading: bool = False) -> None:
    for item in candidates:
        add_event(item, message, momentum * random.uniform(0.75, 1.35), duration, volatility_boost, market, misleading=misleading)


def maybe_global_story(market: dict, event_frequency: float) -> None:
    assets = market.get("assets", [])
    if not assets:
        return

    if random.random() < RARE_GLOBAL_STORY_CHANCE * event_frequency:
        commodities = [item for item in assets if item.get("category") == "Commodity" or item.get("sector") == "Energy"]
        if commodities:
            message = "War breaks out near a major shipping corridor and oil-linked prices skyrocket"
            body = (
                "Energy Sentinel reports that fighting near a shipping route has forced traders to price in a sudden supply shock.\n\n"
                "Commodity and energy-linked assets may surge first, but the broader market can become unstable if inflation fears spread.\n\n"
                "Investment insight: this is a rare high-impact story. Momentum can be profitable, but entries after the first spike are risky."
            )
            append_news(
                market,
                message,
                "MARKET",
                "Commodity",
                0.045,
                10,
                title="Rare shock: conflict sends oil and commodity prices sharply higher",
                body=body,
                source={"name": "Energy Sentinel", "type": "Newspaper", "credibility": 0.84, "image_key": "oil"},
                image_key="oil",
            )
            apply_story_to_assets(market, commodities, message, 0.045, 10, 0.02)
        return

    if random.random() > GLOBAL_STORY_CHANCE * event_frequency:
        return

    story_type = random.choice(["space", "mars", "influencer", "macro", "rotation"])
    if story_type == "space":
        candidates = [item for item in assets if item.get("sector") in {"Technology", "Industrial"}]
        message = "Moon infrastructure contracts spark optimism in technology and industrial suppliers"
        body = (
            "Frontier Briefing says several governments are discussing lunar logistics contracts. Traders are watching robotics, cloud, aerospace, and industrial suppliers.\n\n"
            "Investment insight: technology and industrial assets may benefit, but only companies already showing strength usually hold the gains."
        )
        append_news(market, message, "MARKET", "Market", 0.018, 7, title="We are going back to the Moon, and suppliers could benefit", body=body, source={"name": "Frontier Briefing", "type": "Science Desk", "credibility": 0.74, "image_key": "space"}, image_key="space")
        apply_story_to_assets(market, candidates, message, 0.018, 7, 0.006)
    elif story_type == "mars":
        candidates = [item for item in assets if item.get("sector") in {"Technology", "Industrial"}]
        message = "Mars mission supply rumors lift robotics, cloud, and aerospace-linked names"
        body = (
            "A research note claims the next Mars program will require autonomous systems, secure cloud infrastructure, and advanced transport suppliers.\n\n"
            "Investment insight: this favors long-horizon growth assets, but speculative space headlines often fade if no contract follows."
        )
        append_news(market, message, "MARKET", "Market", 0.015, 6, title="Mars supply chain watch: traders chase frontier technology", body=body, source={"name": "MacroScope", "type": "Research Blog", "credibility": 0.67, "image_key": "space"}, image_key="space")
        apply_story_to_assets(market, candidates, message, 0.015, 6, 0.007)
    elif story_type == "influencer":
        item = random.choice(assets)
        misleading = random.random() < 0.45
        claimed_momentum = 0.04
        actual_momentum = -0.035 if misleading else 0.025
        message = f"FinTube creator tells viewers to invest in {item['symbol']} before the crowd catches on"
        body = (
            f"A viral video claims {item['symbol']} is about to run. The creator points to social momentum and short-term chart movement, but gives little balance-sheet detail.\n\n"
            f"Investment insight: {'This looks misleading; the crowd may be exit liquidity if the price turns.' if misleading else 'The hype may create a short move, but use strict risk controls.'}"
        )
        append_news(
            market,
            message,
            item["symbol"],
            item.get("category", "Market"),
            claimed_momentum,
            5,
            title=f"YouTuber says invest in {item['symbol']} now",
            body=body,
            source={"name": "FinTube Alpha", "type": "YouTuber", "credibility": 0.29 if misleading else 0.43, "image_key": "youtuber"},
            image_key="youtuber",
            misleading=misleading,
        )
        add_event(item, message, actual_momentum, 5, 0.018, market, misleading=misleading)
    elif story_type == "macro":
        candidates = [item for item in assets if item.get("category") in {"Stock", "Fund"}]
        momentum = random.choice([-0.014, 0.014])
        message = "Global inflation report changes expectations for rates and risk assets"
        body = (
            "Daily Ledger reports that traders are repricing interest-rate expectations after a surprise macro reading.\n\n"
            "Investment insight: funds and large stocks often react first. The direction matters less than whether the next few ticks confirm it."
        )
        append_news(market, message, "MARKET", "Market", momentum, 6, title="Global macro report moves rate-sensitive assets", body=body, source={"name": "Daily Ledger", "type": "Newspaper", "credibility": 0.79, "image_key": "globe"}, image_key="globe")
        apply_story_to_assets(market, candidates, message, momentum, 6, 0.006)
    else:
        category = random.choice(["Crypto", "FNT", "Fund", "Stock"])
        candidates = [item for item in assets if item.get("category") == category]
        if not candidates:
            return
        message = f"Retail traders rotate toward {category.lower()} after viral market thread"
        body = (
            f"Street Chatter says retail traders are moving into {category.lower()} assets. The story may create momentum, but social rotations can reverse quickly.\n\n"
            "Investment insight: useful for spotting attention, not a complete trading thesis."
        )
        append_news(market, message, "MARKET", category, 0.018, 4, title=f"Social feed: traders pile into {category.lower()} names", body=body, source={"name": "Street Chatter", "type": "Social Feed", "credibility": 0.36, "image_key": "youtuber"}, image_key="youtuber", misleading=random.random() < 0.25)
        apply_story_to_assets(market, candidates, message, 0.018, 4, 0.01)


def advance_market(market: dict, ticks: int = 1) -> None:
    settings = market.setdefault("settings", {})
    volatility_multiplier = float(settings.get("volatility_multiplier", 1.0))
    event_frequency = float(settings.get("event_frequency", 1.0))
    for _ in range(max(1, ticks)):
        market["_news_created_this_tick"] = 0
        market["_news_cooldown_ticks"] = max(0, int(market.get("_news_cooldown_ticks", 0) or 0) - 1)
        maybe_global_story(market, event_frequency)
        maybe_market_event(market, event_frequency)
        for item in market["assets"]:
            item.setdefault("sector", random.choice(SECTORS.get(item.get("category", "Stock"), ["General"])))
            item["event_cooldown"] = max(0, item.get("event_cooldown", 0) - 1)
            maybe_asset_event(item, market, event_frequency)

            momentum = item.get("event_momentum", 0.0) if item.get("event_momentum_ticks", 0) > 0 else 0.0
            if item.get("event_momentum_ticks", 0) > 0:
                item["event_momentum_ticks"] -= 1
                item["event_momentum"] *= 0.82
            temp_volatility = item.get("temporary_volatility", 0.0)
            if temp_volatility:
                item["temporary_volatility"] = max(0.0, temp_volatility * 0.75)

            volatility = (item.get("volatility", 0.03) + temp_volatility) * volatility_multiplier
            shock = random.gauss(item.get("trend", 0) + momentum, volatility)
            cycle = math.sin(time.time() / 40 + len(item["symbol"])) * 0.006
            cap = max_asset_price(item)
            new_price = max(0.25, item["price"] * (1 + shock + cycle))
            if new_price > cap:
                new_price = cap
                item["event_momentum"] = min(item.get("event_momentum", 0.0), 0.0)
                item["news"] = f"{item['symbol']} hits an overheated valuation ceiling"
            item["price"] = round(new_price, 2)
            history = item.setdefault("history", [])
            history.append(item["price"])
            del history[:-MAX_HISTORY]
            if abs(shock) > volatility * 1.4:
                direction = "rallies" if shock > 0 else "slides"
                item["news"] = f"{item['symbol']} {direction} after heavy trading"
    market["last_tick"] = time.time()
