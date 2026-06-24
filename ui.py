from __future__ import annotations

import platform
import random
import time
from tkinter import BOTH, END, LEFT, RIGHT, X, Y, BooleanVar, Canvas, Label, Listbox, StringVar, Tk, Toplevel, messagebox, simpledialog
from tkinter import ttk

from config import APP_SETTINGS_FILE, CHART_RANGES, DATA_DIR, MARKET_FILE, STARTING_CURRENCY, USERS_FILE, money
from i18n import LANGUAGES, THEMES, TRANSLATIONS
from market import advance_market, generate_market
from storage import (
    Session,
    create_user_record,
    ensure_data_dir,
    hash_password,
    load_json,
    normalize_market_data,
    normalize_users_data,
    save_json,
    verify_password,
)

TRADING_MODES = ("sandbox", "realistic", "fast_realistic")
LOAN_OPTIONS = {
    "loan": {"rate": 0.08, "label_key": "loan"},
    "credit": {"rate": 0.15, "label_key": "credit"},
}
CREDIT_LIMIT_BASE = 100.0
CREDIT_LIMIT_SCORE_MULTIPLIER = 0.8
MINIMUM_PAYMENT_RATE = 0.12
LATE_FEE_RATE = 0.03
DEFAULT_PENALTY_RATE = 0.10
MARGIN_MAX_EQUITY_RATIO = 0.50
MAINTENANCE_MARGIN_RATE = 0.30
SHORT_COLLATERAL_RATE = 0.50
INSURANCE_PREMIUM_RATE = 0.04
INSURANCE_PAYOUT_RATE = 0.50
CORE_ACHIEVEMENTS = [
    ("first_trade", "ach_first_trade_title", "ach_first_trade_desc"),
    ("profit_start", "ach_profit_start_title", "ach_profit_start_desc"),
    ("diversified", "ach_diversified_title", "ach_diversified_desc"),
    ("borrower", "ach_borrower_title", "ach_borrower_desc"),
    ("debt_free", "ach_debt_free_title", "ach_debt_free_desc"),
    ("order_master", "ach_order_master_title", "ach_order_master_desc"),
    ("market_reader", "ach_market_reader_title", "ach_market_reader_desc"),
    ("local_leader", "ach_local_leader_title", "ach_local_leader_desc"),
]
ADDITIONAL_ACHIEVEMENTS = [
    ("trade_5", "Five Trades", "Complete 5 buy or sell transactions.", "trade_count", 5),
    ("trade_10", "Ten Trades", "Complete 10 buy or sell transactions.", "trade_count", 10),
    ("trade_25", "Active Trader", "Complete 25 buy or sell transactions.", "trade_count", 25),
    ("trade_50", "Market Regular", "Complete 50 buy or sell transactions.", "trade_count", 50),
    ("trade_100", "Trading Veteran", "Complete 100 buy or sell transactions.", "trade_count", 100),
    ("buy_5", "Buyer I", "Make 5 buy transactions.", "buy_count", 5),
    ("buy_20", "Buyer II", "Make 20 buy transactions.", "buy_count", 20),
    ("buy_50", "Buyer III", "Make 50 buy transactions.", "buy_count", 50),
    ("sell_5", "Seller I", "Make 5 sell transactions.", "sell_count", 5),
    ("sell_20", "Seller II", "Make 20 sell transactions.", "sell_count", 20),
    ("sell_50", "Seller III", "Make 50 sell transactions.", "sell_count", 50),
    ("portfolio_1", "First Holding", "Hold at least 1 asset.", "portfolio_count", 1),
    ("portfolio_5", "Collector", "Hold at least 5 different assets.", "portfolio_count", 5),
    ("portfolio_10", "Wide Basket", "Hold at least 10 different assets.", "portfolio_count", 10),
    ("portfolio_20", "Index Builder", "Hold at least 20 different assets.", "portfolio_count", 20),
    ("networth_125", "Worth 125", "Reach 125 FC net worth.", "net_worth", 125),
    ("networth_150", "Worth 150", "Reach 150 FC net worth.", "net_worth", 150),
    ("networth_200", "Worth 200", "Reach 200 FC net worth.", "net_worth", 200),
    ("networth_300", "Worth 300", "Reach 300 FC net worth.", "net_worth", 300),
    ("networth_500", "Worth 500", "Reach 500 FC net worth.", "net_worth", 500),
    ("cash_100", "Cash Cushion", "Hold 100 FC in cash.", "cash", 100),
    ("cash_250", "Cash Reserve", "Hold 250 FC in cash.", "cash", 250),
    ("cash_500", "Cash Fortress", "Hold 500 FC in cash.", "cash", 500),
    ("orders_1", "Order Placed", "Place or trigger 1 order.", "order_activity", 1),
    ("orders_5", "Order Planner", "Place or trigger 5 orders.", "order_activity", 5),
    ("orders_10", "Order Strategist", "Place or trigger 10 orders.", "order_activity", 10),
    ("orders_25", "Automation Pro", "Place or trigger 25 orders.", "order_activity", 25),
    ("news_1", "Headline Reader", "Read 1 news article.", "news_read_count", 1),
    ("news_10", "Briefing Habit", "Read 10 news articles.", "news_read_count", 10),
    ("news_25", "Research Desk", "Read 25 news articles.", "news_read_count", 25),
    ("news_50", "News Analyst", "Read 50 news articles.", "news_read_count", 50),
    ("loan_1", "First Funding", "Take 1 loan or credit.", "loan_count", 1),
    ("loan_3", "Bank Customer", "Take 3 loans or credits.", "loan_count", 3),
    ("loan_5", "Credit Operator", "Take 5 loans or credits.", "loan_count", 5),
    ("repay_1", "First Repayment", "Make 1 bank repayment.", "repay_count", 1),
    ("repay_3", "Repayment Habit", "Make 3 bank repayments.", "repay_count", 3),
    ("repay_10", "Reliable Payer", "Make 10 bank repayments.", "repay_count", 10),
    ("debt_100", "Leverage 100", "Carry at least 100 FC of bank debt.", "debt", 100),
    ("debt_250", "Leverage 250", "Carry at least 250 FC of bank debt.", "debt", 250),
    ("transactions_25", "Busy Ledger", "Record 25 total transactions.", "transaction_count", 25),
    ("transactions_75", "Thick Ledger", "Record 75 total transactions.", "transaction_count", 75),
    ("transactions_150", "Archive Builder", "Record 150 total transactions.", "transaction_count", 150),
    ("stocks_3", "Stock Picker", "Hold 3 stocks.", "stock_holdings", 3),
    ("crypto_2", "Crypto Curious", "Hold 2 crypto assets.", "crypto_holdings", 2),
    ("fund_2", "Fund Allocator", "Hold 2 funds.", "fund_holdings", 2),
    ("commodity_2", "Commodity Watcher", "Hold 2 commodities.", "commodity_holdings", 2),
    ("fnt_2", "Collector Market", "Hold 2 FNT assets.", "fnt_holdings", 2),
    ("profit_10", "Ten Percent Up", "Reach 110 FC net worth.", "net_worth", 110),
    ("profit_50", "Fifty Percent Up", "Reach 150 FC net worth.", "net_worth", 150),
    ("double_money", "Double Up", "Reach 200 FC net worth.", "net_worth", 200),
]
ACHIEVEMENTS = CORE_ACHIEVEMENTS + [(item[0], item[1], item[2]) for item in ADDITIONAL_ACHIEVEMENTS]
MARKET_SORTS = [
    ("symbol", "sort_symbol"),
    ("name", "sort_name"),
    ("price", "sort_price"),
    ("change", "sort_change"),
]


class Tooltip:
    def __init__(self, widget, text_getter) -> None:
        self.widget = widget
        self.text_getter = text_getter
        self.tip: Toplevel | None = None
        self.after_id: str | None = None
        widget.bind("<Enter>", self.schedule)
        widget.bind("<Leave>", self.hide)
        widget.bind("<ButtonPress>", self.hide)

    def schedule(self, _event=None) -> None:
        self.hide()
        self.after_id = self.widget.after(450, self.show)

    def show(self) -> None:
        text = self.text_getter()
        if not text:
            return
        x = self.widget.winfo_rootx() + 18
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.tip = Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        Label(self.tip, text=text, justify=LEFT, background="#111827", foreground="#f9fafb", borderwidth=1, relief="solid", padx=8, pady=4).pack()

    def hide(self, _event=None) -> None:
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.tip:
            self.tip.destroy()
            self.tip = None

class VirtualStockMarketApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("Virtual Stock Market")
        self.root.geometry("1180x760")
        self.root.minsize(980, 620)
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
        self.session: Session | None = None
        self.selected_symbol = StringVar()
        self.status = StringVar(value="Welcome to the fake currency market.")
        self.live_updates_enabled = False
        self.live_update_job: str | None = None
        self.live_interval_seconds = StringVar(value="3")
        self.registration_mode = StringVar(value="")
        self.trading_mode = StringVar(value="sandbox")
        self.market_sort = StringVar(value="")
        self.speed_preset = StringVar(value="Normal")
        self.volatility_multiplier = StringVar(value="1.0")
        self.event_frequency = StringVar(value="1.0")
        self.news_filter = StringVar(value="All")
        self.order_type = StringVar(value="Limit Buy")
        self.order_symbol = StringVar()
        self.order_quantity = StringVar(value="1")
        self.order_price = StringVar(value="10")
        self.bank_funding_type = StringVar(value="")
        self.bank_amount = StringVar(value="25")
        self.bank_repayment = StringVar(value="25")
        self.margin_amount = StringVar(value="25")
        self.margin_repayment = StringVar(value="25")
        self.short_symbol = StringVar()
        self.short_quantity = StringVar(value="1")
        self.insurance_symbol = StringVar()
        self.language = StringVar(value="English")
        self.dark_mode = BooleanVar(value=False)
        self.sound_effects_enabled = BooleanVar(value=True)
        self.live_button_text = StringVar(value="")
        self.chart_range = StringVar(value="Days")
        self.chart_points: list[dict] = []
        self.portfolio_symbols: list[str] = []
        self.visible_news: list[dict] = []
        self.logo_canvas: Canvas | None = None
        self.effect_canvas: Canvas | None = None
        self.status_label = None
        self.remember_me = BooleanVar(value=False)
        ensure_data_dir()
        self.apply_theme()
        self.update_live_button_text()
        self.show_login()

    def tr(self, key: str, **values) -> str:
        text = TRANSLATIONS.get(self.language.get(), TRANSLATIONS["English"]).get(key, TRANSLATIONS["English"].get(key, key))
        return text.format(**values) if values else text

    def with_icon(self, icon: str, key: str) -> str:
        return f"{icon} {self.tr(key)}"

    def add_tooltip(self, widget, key: str) -> None:
        Tooltip(widget, lambda: self.tr(key))

    def trading_mode_label(self, mode: str) -> str:
        return self.tr(f"mode_{mode}") if mode in TRADING_MODES else self.tr("mode_sandbox")

    def trading_mode_from_label(self, label: str) -> str:
        for mode in TRADING_MODES:
            if label == self.trading_mode_label(mode):
                return mode
        return ""

    def funding_type_label(self, funding_type: str) -> str:
        option = LOAN_OPTIONS.get(funding_type, LOAN_OPTIONS["loan"])
        return self.tr(option["label_key"])

    def funding_type_from_label(self, label: str) -> str:
        for funding_type in LOAN_OPTIONS:
            if label == self.funding_type_label(funding_type):
                return funding_type
        return ""

    def sort_label(self, sort_key: str) -> str:
        return self.tr(next(label_key for key, label_key in MARKET_SORTS if key == sort_key))

    def sort_key_from_label(self, label: str) -> str:
        for sort_key, label_key in MARKET_SORTS:
            if label == self.tr(label_key):
                return sort_key
        return "symbol"

    def current_trading_mode(self) -> str:
        mode = self.trading_mode.get()
        return mode if mode in TRADING_MODES else "sandbox"

    def show_manual_market_controls(self) -> bool:
        return self.current_trading_mode() == "sandbox"

    def show_speed_controls(self) -> bool:
        return self.current_trading_mode() in {"sandbox", "fast_realistic"}

    def colors(self) -> dict:
        return THEMES["dark" if self.dark_mode.get() else "light"]

    def apply_theme(self) -> None:
        colors = self.colors()
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(".", background=colors["bg"], foreground=colors["text"])
        style.configure("TFrame", background=colors["bg"])
        style.configure("TLabel", background=colors["bg"], foreground=colors["text"])
        style.configure("TButton", padding=6, background=colors["panel"], foreground=colors["text"], bordercolor=colors["border"])
        style.map(
            "TButton",
            background=[
                ("disabled", colors["panel"]),
                ("pressed", colors["pressed_bg"]),
                ("active", colors["hover_bg"]),
            ],
            foreground=[
                ("disabled", colors["muted"]),
                ("pressed", colors["select_fg"]),
                ("active", colors["text"]),
            ],
            bordercolor=[("active", colors["select_bg"]), ("pressed", colors["select_bg"])],
        )
        style.configure("TCheckbutton", background=colors["bg"], foreground=colors["text"])
        style.map(
            "TCheckbutton",
            background=[("active", colors["hover_bg"]), ("pressed", colors["pressed_bg"]), ("selected", colors["bg"])],
            foreground=[("active", colors["text"]), ("pressed", colors["select_fg"]), ("disabled", colors["muted"])],
        )
        style.configure("TRadiobutton", background=colors["bg"], foreground=colors["text"])
        style.map(
            "TRadiobutton",
            background=[("active", colors["hover_bg"]), ("pressed", colors["pressed_bg"]), ("selected", colors["bg"])],
            foreground=[("active", colors["text"]), ("pressed", colors["select_fg"]), ("disabled", colors["muted"])],
        )
        style.configure(
            "TEntry",
            fieldbackground=colors["field_bg"],
            foreground=colors["field_fg"],
            insertcolor=colors["field_fg"],
            bordercolor=colors["border"],
            lightcolor=colors["border"],
            darkcolor=colors["border"],
        )
        style.map(
            "TEntry",
            fieldbackground=[("disabled", colors["panel"]), ("readonly", colors["field_bg"]), ("focus", colors["field_bg"])],
            foreground=[("disabled", colors["muted"]), ("readonly", colors["field_fg"]), ("focus", colors["field_fg"])],
            selectbackground=[("focus", colors["field_select_bg"])],
            selectforeground=[("focus", colors["field_select_fg"])],
        )
        style.configure(
            "TCombobox",
            fieldbackground=colors["field_bg"],
            background=colors["field_bg"],
            foreground=colors["field_fg"],
            arrowcolor=colors["field_fg"],
            bordercolor=colors["border"],
            lightcolor=colors["border"],
            darkcolor=colors["border"],
        )
        style.map(
            "TCombobox",
            fieldbackground=[
                ("active", colors["field_bg"]),
                ("readonly", colors["field_bg"]),
                ("focus", colors["field_bg"]),
                ("disabled", colors["panel"]),
            ],
            background=[("active", colors["hover_bg"]), ("pressed", colors["pressed_bg"])],
            foreground=[
                ("active", colors["field_fg"]),
                ("readonly", colors["field_fg"]),
                ("focus", colors["field_fg"]),
                ("disabled", colors["muted"]),
            ],
            selectbackground=[("readonly", colors["field_select_bg"]), ("focus", colors["field_select_bg"])],
            selectforeground=[("readonly", colors["field_select_fg"]), ("focus", colors["field_select_fg"])],
            arrowcolor=[("disabled", colors["muted"]), ("active", colors["field_fg"]), ("readonly", colors["field_fg"])],
        )
        style.configure("TNotebook", background=colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", padding=(12, 6), background=colors["panel"], foreground=colors["text"])
        style.map(
            "TNotebook.Tab",
            background=[("selected", colors["select_bg"]), ("active", colors["hover_bg"])],
            foreground=[("selected", colors["select_fg"]), ("active", colors["text"])],
        )
        self.root.option_add("*TCombobox*Listbox.background", colors["field_bg"])
        self.root.option_add("*TCombobox*Listbox.foreground", colors["field_fg"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", colors["field_select_bg"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", colors["field_select_fg"])
        try:
            self.root.configure(background=colors["bg"])
        except Exception:
            pass

    def configure_listbox(self, listbox: Listbox) -> None:
        colors = self.colors()
        listbox.configure(
            background=colors["list_bg"],
            foreground=colors["list_fg"],
            selectbackground=colors["select_bg"],
            selectforeground=colors["select_fg"],
            highlightbackground=colors["border"],
            highlightcolor=colors["border"],
        )

    def play_sound(self, kind: str = "success") -> None:
        if not self.sound_effects_enabled.get():
            return
        patterns = {
            "success": [0],
            "trade": [0, 90],
            "sell": [0, 75],
            "order": [0, 120],
            "achievement": [0, 90, 180],
            "risk": [0, 140],
            "error": [0],
        }
        for delay in patterns.get(kind, patterns["success"]):
            self.root.after(delay, self.root.bell)

    def flash_status(self, kind: str = "success") -> None:
        if not self.status_label:
            return
        colors = {
            "success": "#16a34a",
            "trade": "#2563eb",
            "sell": "#dc2626",
            "order": "#7c3aed",
            "achievement": "#d97706",
            "risk": "#dc2626",
            "error": "#b91c1c",
        }
        self.status_label.configure(foreground=colors.get(kind, colors["success"]))
        self.root.after(900, lambda: self.status_label.configure(foreground=self.colors()["muted"]) if self.status_label else None)

    def pulse_effect(self, kind: str = "success", label: str = "") -> None:
        if not self.effect_canvas:
            return
        canvas = self.effect_canvas
        canvas.delete("effect")
        colors = {
            "success": "#22c55e",
            "trade": "#3b82f6",
            "sell": "#ef4444",
            "order": "#8b5cf6",
            "achievement": "#f59e0b",
            "risk": "#dc2626",
            "error": "#ef4444",
        }
        color = colors.get(kind, "#22c55e")
        width = max(canvas.winfo_width(), 220)
        height = 64
        for index in range(7):
            x = 12 + index * ((width - 24) / 6)
            bar_height = random.randint(14, 46)
            canvas.create_rectangle(x - 5, height - 8, x + 5, height - 8 - bar_height, fill=color, outline="", tags="effect")
        canvas.create_text(width / 2, 14, text=label, fill=color, font=("Arial", 10, "bold"), tags="effect")

        def fade(step: int = 0) -> None:
            if not self.effect_canvas:
                return
            if step >= 7:
                self.effect_canvas.delete("effect")
                return
            offset = step + 1
            for item_id in self.effect_canvas.find_withtag("effect"):
                self.effect_canvas.move(item_id, 0, -1 if step < 3 else 1)
            self.root.after(80 + offset * 8, lambda: fade(step + 1))

        fade()

    def confetti_effect(self) -> None:
        if not self.effect_canvas:
            return
        canvas = self.effect_canvas
        canvas.delete("confetti")
        width = max(canvas.winfo_width(), 220)
        palette = ["#f59e0b", "#22c55e", "#3b82f6", "#ef4444", "#a855f7", "#06b6d4"]
        pieces = []
        for _ in range(28):
            x = random.randint(8, int(width) - 8)
            y = random.randint(-42, 8)
            size = random.randint(3, 7)
            color = random.choice(palette)
            item_id = canvas.create_rectangle(x, y, x + size, y + size, fill=color, outline="", tags="confetti")
            pieces.append((item_id, random.uniform(-1.6, 1.6), random.uniform(2.2, 4.8)))

        def fall(step: int = 0) -> None:
            if not self.effect_canvas:
                return
            if step >= 28:
                self.effect_canvas.delete("confetti")
                return
            for item_id, dx, dy in pieces:
                self.effect_canvas.move(item_id, dx, dy)
            self.root.after(45, lambda: fall(step + 1))

        fall()

    def trigger_effect(self, kind: str = "success", label: str = "", sound: str | None = None) -> None:
        self.play_sound(sound or kind)
        self.flash_status(kind)
        self.pulse_effect(kind, label)

    def pulse_chart_latest(self, kind: str = "trade") -> None:
        if not hasattr(self, "chart") or not self.chart_points:
            return
        point = self.chart_points[-1]
        color = "#16a34a" if kind in {"success", "trade"} else "#dc2626" if kind in {"sell", "risk"} else "#2563eb"

        def draw(step: int = 0) -> None:
            if not hasattr(self, "chart") or step >= 6:
                if hasattr(self, "chart"):
                    self.chart.delete("pulse")
                return
            self.chart.delete("pulse")
            radius = 6 + step * 5
            self.chart.create_oval(
                point["x"] - radius,
                point["y"] - radius,
                point["x"] + radius,
                point["y"] + radius,
                outline=color,
                width=max(1, 4 - step // 2),
                tags="pulse",
            )
            self.root.after(70, lambda: draw(step + 1))

        draw()

    def update_live_button_text(self) -> None:
        key = "freeze" if self.live_updates_enabled else "resume"
        icon = "⏸" if self.live_updates_enabled else "▶"
        self.live_button_text.set(self.with_icon(icon, key))

    def ensure_user_settings(self) -> dict:
        user = self.session.user
        settings = user.setdefault("settings", {})
        settings.setdefault("language", "English")
        settings.setdefault("dark_mode", False)
        settings.setdefault("sound_effects_enabled", True)
        settings.setdefault("trading_mode", "sandbox")
        settings.setdefault("live_interval_seconds", 3.0)
        return settings

    def load_user_preferences(self) -> None:
        settings = self.ensure_user_settings()
        language = settings.get("language", "English")
        self.language.set(language if language in LANGUAGES else "English")
        self.dark_mode.set(bool(settings.get("dark_mode", False)))
        self.sound_effects_enabled.set(bool(settings.get("sound_effects_enabled", True)))
        mode = settings.get("trading_mode", "sandbox")
        self.trading_mode.set(mode if mode in TRADING_MODES else "sandbox")
        interval = 1.0 if self.current_trading_mode() == "realistic" else float(settings.get("live_interval_seconds", 3.0))
        self.live_interval_seconds.set(f"{interval:g}")
        self.apply_theme()
        self.update_live_button_text()

    def save_user_preferences(self) -> None:
        if not self.session:
            return
        settings = self.ensure_user_settings()
        settings["language"] = self.language.get()
        settings["dark_mode"] = bool(self.dark_mode.get())
        settings["sound_effects_enabled"] = bool(self.sound_effects_enabled.get())
        settings["trading_mode"] = self.current_trading_mode()
        if self.current_trading_mode() != "realistic":
            settings["live_interval_seconds"] = self.current_interval_seconds(show_errors=False)
        self.session.save()

    def load_app_settings(self) -> dict:
        return load_json(APP_SETTINGS_FILE, {"remembered_username": ""})

    def save_remembered_username(self, username: str) -> None:
        save_json(APP_SETTINGS_FILE, {"remembered_username": username if self.remember_me.get() else ""})

    def now_stamp(self) -> tuple[float, str]:
        timestamp = time.time()
        return timestamp, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

    def clear(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()

    def show_login(self) -> None:
        self.clear()
        shell = ttk.Frame(self.root, padding=36)
        shell.pack(expand=True, fill=BOTH)

        card = ttk.Frame(shell, padding=28)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(card, text=self.tr("app_title"), font=("Arial", 26, "bold")).pack(pady=(0, 8))
        ttk.Label(card, text=self.tr("login_subtitle")).pack(pady=(0, 22))

        app_settings = self.load_app_settings()
        remembered_username = app_settings.get("remembered_username", "")
        self.remember_me.set(bool(remembered_username))
        username = StringVar(value=remembered_username)
        password = StringVar()
        fields = ttk.Frame(card)
        fields.pack(fill=X)
        ttk.Label(fields, text=self.tr("username")).pack(anchor="w")
        ttk.Entry(fields, textvariable=username, width=34).pack(fill=X, pady=(2, 10))
        ttk.Label(fields, text=self.tr("password")).pack(anchor="w")
        ttk.Entry(fields, textvariable=password, width=34, show="*").pack(fill=X, pady=(2, 8))
        self.registration_mode.set("")
        ttk.Label(fields, text=self.tr("registration_trading_mode")).pack(anchor="w")
        ttk.Combobox(
            fields,
            textvariable=self.registration_mode,
            values=[self.trading_mode_label(mode) for mode in TRADING_MODES],
            state="readonly",
            width=32,
        ).pack(fill=X, pady=(2, 8))
        ttk.Checkbutton(fields, text=self.tr("remember_me"), variable=self.remember_me).pack(anchor="w", pady=(0, 18))

        buttons = ttk.Frame(card)
        buttons.pack(fill=X)
        ttk.Button(buttons, text=self.with_icon("🔐", "login"), command=lambda: self.login(username.get(), password.get())).pack(side=LEFT, expand=True, fill=X, padx=(0, 6))
        ttk.Button(buttons, text=self.with_icon("＋", "register"), command=lambda: self.register(username.get(), password.get())).pack(side=RIGHT, expand=True, fill=X, padx=(6, 0))

        ttk.Label(card, text=self.tr("local_files"), foreground=self.colors()["muted"]).pack(pady=(18, 0))

    def load_session(self, username: str) -> Session:
        market = normalize_market_data(load_json(MARKET_FILE, {"last_tick": time.time(), "assets": generate_market()}))
        users = normalize_users_data(load_json(USERS_FILE, {"users": {}}))
        session = Session(username=username, users_data=users, market_data=market)
        self.apply_login_market_progress(session)
        return session

    def apply_login_market_progress(self, session: Session) -> None:
        user = session.user
        settings = user.setdefault("settings", {})
        mode = settings.get("trading_mode", "sandbox")
        login_ts, login_at = self.now_stamp()
        closed_ts = float(user.get("last_closed_at_ts") or 0.0)
        closed_at = user.get("last_closed_at", "")
        market_last_tick = float(session.market_data.get("last_tick", login_ts))
        ticks = 0

        if mode in {"realistic", "fast_realistic"} and closed_ts > 0:
            try:
                interval = 1.0 if mode == "realistic" else float(settings.get("live_interval_seconds", 3.0) or 3.0)
            except (TypeError, ValueError):
                interval = 3.0
            interval = min(max(interval, 0.5), 60.0)
            elapsed = max(0.0, login_ts - max(closed_ts, market_last_tick))
            ticks = int(elapsed // interval)
            if ticks > 0:
                advance_market(session.market_data, ticks=ticks)
        else:
            elapsed = int((login_ts - market_last_tick) // 15)
            ticks = min(max(elapsed, 1), 10)
            advance_market(session.market_data, ticks=ticks)

        user["last_login_at"] = login_at
        user["last_login_at_ts"] = login_ts
        user["last_offline_summary"] = {
            "closed_at": closed_at,
            "login_at": login_at,
            "mode": mode,
            "ticks": ticks,
        }

    def register(self, username: str, password: str) -> None:
        username = username.strip().lower()
        trading_mode = self.trading_mode_from_label(self.registration_mode.get())
        if len(username) < 3 or not username.replace("_", "").isalnum():
            messagebox.showerror("Registration failed", "Use at least 3 letters, numbers, or underscores.")
            return
        if len(password) < 4:
            messagebox.showerror("Registration failed", "Use a password with at least 4 characters.")
            return
        if trading_mode not in TRADING_MODES:
            messagebox.showerror(self.tr("registration_failed"), self.tr("select_trading_mode_error"))
            return
        users = load_json(USERS_FILE, {"users": {}})
        if username in users["users"]:
            messagebox.showerror("Registration failed", "That username already exists.")
            return
        users["users"][username] = create_user_record(username, password)
        users["users"][username]["settings"]["trading_mode"] = trading_mode
        if trading_mode == "realistic":
            users["users"][username]["settings"]["live_interval_seconds"] = 1.0
        save_json(USERS_FILE, users)
        self.save_remembered_username(username)
        self.session = self.load_session(username)
        self.load_user_preferences()
        self.status.set(f"Registered {username}. Starting balance: {money(STARTING_CURRENCY)}.")
        self.show_dashboard()

    def login(self, username: str, password: str) -> None:
        username = username.strip().lower()
        users = load_json(USERS_FILE, {"users": {}})
        record = users["users"].get(username)
        if not record or not verify_password(password, record):
            messagebox.showerror("Login failed", "Username or password is incorrect.")
            return
        self.save_remembered_username(username)
        self.session = self.load_session(username)
        self.load_user_preferences()
        summary = self.session.user.get("last_offline_summary", {})
        if summary.get("closed_at") and self.current_trading_mode() in {"realistic", "fast_realistic"}:
            self.status.set(
                self.tr(
                    "offline_progress_status",
                    username=username,
                    closed_at=summary.get("closed_at", ""),
                    login_at=summary.get("login_at", ""),
                    ticks=summary.get("ticks", 0),
                )
            )
        else:
            self.status.set(f"Welcome back, {username}.")
        self.show_dashboard()

    def draw_logo(self, parent) -> None:
        colors = self.colors()
        self.logo_canvas = Canvas(parent, width=220, height=92, highlightthickness=0, background=colors["bg"])
        self.logo_canvas.pack(anchor="w", pady=(0, 12))
        self.logo_canvas.create_oval(10, 12, 82, 84, fill="#2563eb", outline="")
        self.logo_canvas.create_line(28, 58, 42, 44, 54, 52, 70, 28, fill="#ffffff", width=4, smooth=True)
        self.logo_canvas.create_oval(65, 23, 75, 33, fill="#22c55e", outline="")
        self.logo_canvas.create_text(98, 34, anchor="w", text="VSM", fill=colors["text"], font=("Arial", 24, "bold"))
        self.logo_canvas.create_text(100, 60, anchor="w", text=self.tr("app_title"), fill=colors["muted"], font=("Arial", 10))

    def show_dashboard(self, start_live: bool = True) -> None:
        if self.live_update_job:
            self.root.after_cancel(self.live_update_job)
            self.live_update_job = None
        self.apply_theme()
        self.root.title(self.tr("app_title"))
        market_settings = self.session.market_data.setdefault("settings", {})
        self.volatility_multiplier.set(f"{float(market_settings.get('volatility_multiplier', 1.0)):g}")
        self.event_frequency.set(f"{float(market_settings.get('event_frequency', 1.0)):g}")
        self.clear()
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self.root, padding=14)
        sidebar.grid(row=0, column=0, sticky="ns")
        main = ttk.Frame(self.root, padding=14)
        main.grid(row=0, column=1, sticky="nsew")
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)

        self.draw_logo(sidebar)
        ttk.Label(sidebar, text=self.tr("account"), font=("Arial", 18, "bold")).pack(anchor="w", pady=(0, 10))
        self.account_label = ttk.Label(sidebar, text="")
        self.account_label.pack(anchor="w", pady=(0, 16))
        ttk.Label(sidebar, text=f"{self.tr('trading_mode')}: {self.trading_mode_label(self.current_trading_mode())}", foreground=self.colors()["muted"]).pack(anchor="w", pady=(0, 10))
        if self.show_manual_market_controls():
            manual_button = ttk.Button(sidebar, text=self.with_icon("▶", "manual_tick"), command=self.tick)
            manual_button.pack(fill=X, pady=3)
            self.add_tooltip(manual_button, "tooltip_manual_tick")
            live_button = ttk.Button(sidebar, textvariable=self.live_button_text, command=self.toggle_live_updates)
            live_button.pack(fill=X, pady=3)
            self.add_tooltip(live_button, "tooltip_freeze")

        if self.show_speed_controls():
            speed_frame = ttk.Frame(sidebar)
            speed_frame.pack(fill=X, pady=(8, 3))
            ttk.Label(speed_frame, text=self.tr("step_speed")).pack(anchor="w")
            ttk.Entry(speed_frame, textvariable=self.live_interval_seconds, width=8).pack(side=LEFT, fill=X, expand=True, pady=(2, 0))
            speed_button = ttk.Button(speed_frame, text=self.with_icon("✓", "apply"), command=self.apply_live_speed)
            speed_button.pack(side=RIGHT, padx=(6, 0), pady=(2, 0))
            self.add_tooltip(speed_button, "tooltip_speed")

        refresh_button = ttk.Button(sidebar, text=self.with_icon("↻", "refresh"), command=self.refresh_all)
        refresh_button.pack(fill=X, pady=3)
        self.add_tooltip(refresh_button, "tooltip_refresh")
        logout_button = ttk.Button(sidebar, text=self.with_icon("⇥", "logout"), command=self.logout)
        logout_button.pack(fill=X, pady=(20, 3))
        self.add_tooltip(logout_button, "tooltip_logout")
        self.status_label = ttk.Label(sidebar, textvariable=self.status, wraplength=220, foreground=self.colors()["muted"])
        self.status_label.pack(anchor="w", pady=(24, 6))
        self.effect_canvas = Canvas(sidebar, width=220, height=64, highlightthickness=0, background=self.colors()["bg"])
        self.effect_canvas.pack(anchor="w", fill=X)

        notebook = ttk.Notebook(main)
        notebook.grid(row=0, column=0, sticky="nsew")
        home_tab = ttk.Frame(notebook, padding=14)
        market_tab = ttk.Frame(notebook, padding=14)
        settings_tab = ttk.Frame(notebook, padding=14)
        bank_tab = ttk.Frame(notebook, padding=14)
        achievements_tab = ttk.Frame(notebook, padding=14)
        history_tab = ttk.Frame(notebook, padding=14)
        performance_tab = ttk.Frame(notebook, padding=14)
        orders_tab = ttk.Frame(notebook, padding=14)
        news_tab = ttk.Frame(notebook, padding=14)
        leaderboard_tab = ttk.Frame(notebook, padding=14)
        home_tab.columnconfigure(0, weight=1)
        home_tab.columnconfigure(1, weight=1)
        home_tab.rowconfigure(1, weight=1)
        home_tab.rowconfigure(2, weight=1)
        home_tab.rowconfigure(3, weight=1)
        market_tab.rowconfigure(2, weight=1)
        market_tab.columnconfigure(0, weight=1)
        notebook.add(home_tab, text=self.with_icon("⌂", "home"))
        notebook.add(market_tab, text=self.with_icon("📈", "market"))
        notebook.add(bank_tab, text=self.with_icon("🏦", "bank"))
        notebook.add(achievements_tab, text=self.with_icon("★", "achievements"))
        notebook.add(performance_tab, text=self.with_icon("📊", "performance"))
        notebook.add(history_tab, text=self.with_icon("🧾", "history"))
        notebook.add(orders_tab, text=self.with_icon("⏱", "orders"))
        notebook.add(news_tab, text=self.with_icon("📰", "news"))
        notebook.add(leaderboard_tab, text=self.with_icon("🏆", "leaderboard"))
        notebook.add(settings_tab, text=self.with_icon("⚙", "settings"))
        self.build_home_tab(home_tab)
        self.build_achievements_tab(achievements_tab)
        self.build_performance_tab(performance_tab)
        self.build_bank_tab(bank_tab)
        self.build_history_tab(history_tab)
        self.build_orders_tab(orders_tab)
        self.build_news_tab(news_tab)
        self.build_leaderboard_tab(leaderboard_tab)
        self.build_settings_tab(settings_tab)

        filters = ttk.Frame(market_tab)
        filters.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(filters, text=self.tr("market"), font=("Arial", 22, "bold")).pack(side=LEFT)
        self.filter_var = StringVar(value="All")
        for category in ["All", "Stock", "Crypto", "FNT", "Commodity", "Fund"]:
            ttk.Radiobutton(filters, text=category, variable=self.filter_var, value=category, command=self.refresh_market_list).pack(side=LEFT, padx=8)
        ttk.Label(filters, text=self.tr("sort_by")).pack(side=LEFT, padx=(18, 4))
        self.market_sort.set(self.sort_label("symbol"))
        sort_box = ttk.Combobox(filters, textvariable=self.market_sort, values=[self.sort_label(key) for key, _label_key in MARKET_SORTS], state="readonly", width=14)
        sort_box.pack(side=LEFT)
        sort_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_market_list())

        panes = ttk.PanedWindow(market_tab, orient="horizontal")
        panes.grid(row=1, column=0, rowspan=2, sticky="nsew")

        market_frame = ttk.Frame(panes, padding=8)
        panes.add(market_frame, weight=2)
        list_frame = ttk.Frame(market_frame)
        list_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.market_list = Listbox(list_frame, height=25, exportselection=False)
        self.market_change_list = Listbox(market_frame, height=25, width=10, exportselection=False)
        self.configure_listbox(self.market_list)
        self.configure_listbox(self.market_change_list)
        self.market_list.pack(side=LEFT, fill=BOTH, expand=True)
        self.market_change_list.pack(side=LEFT, fill=Y)
        scroll = ttk.Scrollbar(market_frame, orient="vertical", command=self.scroll_market_lists)
        scroll.pack(side=RIGHT, fill=Y)
        self.market_list.configure(yscrollcommand=scroll.set)
        self.market_change_list.configure(yscrollcommand=scroll.set)
        self.market_list.bind("<<ListboxSelect>>", self.on_select_asset)
        self.market_change_list.bind("<<ListboxSelect>>", self.on_select_asset)
        self.market_list.bind("<MouseWheel>", self.on_market_mousewheel)
        self.market_change_list.bind("<MouseWheel>", self.on_market_mousewheel)

        detail = ttk.Frame(panes, padding=8)
        panes.add(detail, weight=3)
        self.asset_title = ttk.Label(detail, text=self.tr("select_asset"), font=("Arial", 18, "bold"))
        self.asset_title.pack(anchor="w")
        self.asset_meta = ttk.Label(detail, text="")
        self.asset_meta.pack(anchor="w", pady=(2, 8))

        range_frame = ttk.Frame(detail)
        range_frame.pack(fill=X, pady=(0, 6))
        ttk.Label(range_frame, text=self.tr("chart_range")).pack(side=LEFT, padx=(0, 8))
        for label in CHART_RANGES:
            ttk.Radiobutton(
                range_frame,
                text=label,
                variable=self.chart_range,
                value=label,
                command=self.render_selected,
            ).pack(side=LEFT, padx=4)

        colors = self.colors()
        self.chart = Canvas(detail, height=260, background=colors["bg"], highlightthickness=1, highlightbackground=colors["border"])
        self.chart.pack(fill=X, pady=(4, 12))
        self.chart.bind("<Button-1>", self.on_chart_click)
        self.event_log_label = ttk.Label(detail, text="", wraplength=620, foreground=colors["muted"])
        self.event_log_label.pack(anchor="w", fill=X, pady=(0, 10))

        trade = ttk.Frame(detail)
        trade.pack(fill=X)
        self.quantity = StringVar(value="1")
        ttk.Label(trade, text=self.tr("quantity")).pack(side=LEFT)
        ttk.Entry(trade, textvariable=self.quantity, width=10).pack(side=LEFT, padx=8)
        buy_button = ttk.Button(trade, text=self.with_icon("▲", "buy"), command=self.buy_selected)
        buy_button.pack(side=LEFT, padx=4)
        self.add_tooltip(buy_button, "tooltip_buy")
        sell_button = ttk.Button(trade, text=self.with_icon("▼", "sell"), command=self.sell_selected)
        sell_button.pack(side=LEFT, padx=4)
        self.add_tooltip(sell_button, "tooltip_sell")

        ttk.Label(detail, text=self.tr("portfolio"), font=("Arial", 16, "bold")).pack(anchor="w", pady=(20, 4))
        self.portfolio_list = Listbox(detail, height=8, exportselection=False)
        self.configure_listbox(self.portfolio_list)
        self.portfolio_list.pack(fill=BOTH, expand=True)
        self.portfolio_list.bind("<Double-Button-1>", self.on_portfolio_double_click)

        self.refresh_all()
        self.bind_shortcuts()
        self.maybe_show_tutorial()
        if self.current_trading_mode() in {"realistic", "fast_realistic"}:
            self.start_live_updates()
        elif start_live:
            self.start_live_updates()
        else:
            self.stop_live_updates()

    def build_performance_tab(self, parent) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        ttk.Label(parent, text=self.tr("portfolio_performance"), font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.performance_chart = Canvas(parent, height=320, background=self.colors()["bg"], highlightthickness=1, highlightbackground=self.colors()["border"])
        self.performance_chart.grid(row=1, column=0, sticky="nsew")

    def build_home_tab(self, parent) -> None:
        ttk.Label(parent, text=self.tr("dashboard"), font=("Arial", 22, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        summary_box = ttk.LabelFrame(parent, text=self.tr("account_snapshot"), padding=12)
        summary_box.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))
        summary_box.columnconfigure(0, weight=1)
        summary_box.rowconfigure(2, weight=1)
        self.dashboard_summary = ttk.Label(summary_box, text="", font=("Arial", 12), justify=LEFT)
        self.dashboard_summary.grid(row=0, column=0, sticky="nw")
        ttk.Label(summary_box, text=self.tr("portfolio_allocation"), font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w", pady=(12, 4))
        self.allocation_chart = Canvas(summary_box, height=170, background=self.colors()["bg"], highlightthickness=1, highlightbackground=self.colors()["border"])
        self.allocation_chart.grid(row=2, column=0, sticky="nsew")

        movers_box = ttk.LabelFrame(parent, text=self.tr("biggest_movers"), padding=12)
        movers_box.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(0, 10))
        movers_box.rowconfigure(0, weight=1)
        movers_box.columnconfigure(0, weight=1)
        self.dashboard_movers = Listbox(movers_box, height=9, exportselection=False)
        self.configure_listbox(self.dashboard_movers)
        self.dashboard_movers.grid(row=0, column=0, sticky="nsew")
        self.dashboard_movers.bind("<Double-Button-1>", self.open_dashboard_mover)

        news_box = ttk.LabelFrame(parent, text=self.tr("top_news"), padding=12)
        news_box.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        news_box.rowconfigure(0, weight=1)
        news_box.columnconfigure(0, weight=1)
        self.dashboard_news = Listbox(news_box, height=8, exportselection=False)
        self.configure_listbox(self.dashboard_news)
        self.dashboard_news.grid(row=0, column=0, sticky="nsew")

        alerts_box = ttk.LabelFrame(parent, text=self.tr("risk_alerts"), padding=12)
        alerts_box.grid(row=2, column=1, sticky="nsew", padx=(8, 0))
        alerts_box.rowconfigure(0, weight=1)
        alerts_box.columnconfigure(0, weight=1)
        self.dashboard_alerts = Listbox(alerts_box, height=8, exportselection=False)
        self.configure_listbox(self.dashboard_alerts)
        self.dashboard_alerts.grid(row=0, column=0, sticky="nsew")

        quality_box = ttk.LabelFrame(parent, text=self.tr("news_quality"), padding=12)
        quality_box.grid(row=3, column=0, sticky="nsew", padx=(0, 8), pady=(10, 0))
        quality_box.rowconfigure(0, weight=1)
        quality_box.columnconfigure(0, weight=1)
        self.dashboard_news_quality = Listbox(quality_box, height=5, exportselection=False)
        self.configure_listbox(self.dashboard_news_quality)
        self.dashboard_news_quality.grid(row=0, column=0, sticky="nsew")

        due_box = ttk.LabelFrame(parent, text=self.tr("loan_due_dates"), padding=12)
        due_box.grid(row=3, column=1, sticky="nsew", padx=(8, 0), pady=(10, 0))
        due_box.rowconfigure(0, weight=1)
        due_box.columnconfigure(0, weight=1)
        self.dashboard_loan_due = Listbox(due_box, height=5, exportselection=False)
        self.configure_listbox(self.dashboard_loan_due)
        self.dashboard_loan_due.grid(row=0, column=0, sticky="nsew")

    def build_achievements_tab(self, parent) -> None:
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(1, weight=1)
        ttk.Label(parent, text=self.tr("achievements"), font=("Arial", 22, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        unlocked_box = ttk.LabelFrame(parent, text=self.tr("unlocked_achievements"), padding=12)
        unlocked_box.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        unlocked_box.rowconfigure(0, weight=1)
        unlocked_box.columnconfigure(0, weight=1)
        self.unlocked_achievements_list = Listbox(unlocked_box, height=16, exportselection=False)
        self.configure_listbox(self.unlocked_achievements_list)
        self.unlocked_achievements_list.grid(row=0, column=0, sticky="nsew")

        locked_box = ttk.LabelFrame(parent, text=self.tr("locked_achievements"), padding=12)
        locked_box.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        locked_box.rowconfigure(0, weight=1)
        locked_box.columnconfigure(0, weight=1)
        self.locked_achievements_list = Listbox(locked_box, height=16, exportselection=False)
        self.configure_listbox(self.locked_achievements_list)
        self.locked_achievements_list.grid(row=0, column=0, sticky="nsew")

    def build_history_tab(self, parent) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)
        ttk.Label(parent, text=self.tr("transaction_history"), font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        ttk.Label(parent, text=self.tr("history_header"), foreground=self.colors()["muted"]).grid(row=1, column=0, sticky="w", pady=(0, 4))
        self.transaction_list = Listbox(parent, height=18, exportselection=False)
        self.configure_listbox(self.transaction_list)
        self.transaction_list.grid(row=2, column=0, sticky="nsew")

    def build_bank_tab(self, parent) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(5, weight=1)
        self.bank_funding_type.set(self.funding_type_label("loan"))
        ttk.Label(parent, text=self.tr("bank"), font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.bank_risk_summary = ttk.Label(parent, text="", foreground=self.colors()["muted"], wraplength=900)
        self.bank_risk_summary.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        form = ttk.LabelFrame(parent, text=self.tr("request_funding"), padding=14)
        form.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(form, text=self.tr("funding_type")).pack(side=LEFT)
        ttk.Combobox(
            form,
            textvariable=self.bank_funding_type,
            values=[self.funding_type_label(funding_type) for funding_type in LOAN_OPTIONS],
            state="readonly",
            width=10,
        ).pack(side=LEFT, padx=6)
        ttk.Label(form, text=self.tr("amount")).pack(side=LEFT)
        ttk.Entry(form, textvariable=self.bank_amount, width=10).pack(side=LEFT, padx=6)
        request_button = ttk.Button(form, text=self.with_icon("＋", "request"), command=self.request_bank_funding)
        request_button.pack(side=LEFT, padx=6)
        self.add_tooltip(request_button, "tooltip_bank_request")
        ttk.Label(form, text=self.tr("bank_help"), foreground=self.colors()["muted"]).pack(side=LEFT, padx=10)

        risk_box = ttk.LabelFrame(parent, text=self.tr("risk_tools"), padding=14)
        risk_box.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(risk_box, text=self.tr("margin_amount")).pack(side=LEFT)
        ttk.Entry(risk_box, textvariable=self.margin_amount, width=9).pack(side=LEFT, padx=5)
        margin_button = ttk.Button(risk_box, text=self.with_icon("＋", "request_margin"), command=self.request_margin)
        margin_button.pack(side=LEFT, padx=5)
        self.add_tooltip(margin_button, "tooltip_margin")
        ttk.Label(risk_box, text=self.tr("margin_repayment")).pack(side=LEFT, padx=(12, 0))
        ttk.Entry(risk_box, textvariable=self.margin_repayment, width=9).pack(side=LEFT, padx=5)
        repay_margin_button = ttk.Button(risk_box, text=self.with_icon("✓", "repay_margin"), command=self.repay_margin)
        repay_margin_button.pack(side=LEFT, padx=5)
        self.add_tooltip(repay_margin_button, "tooltip_repay_margin")

        short_box = ttk.Frame(parent)
        short_box.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(short_box, text=self.tr("short_symbol")).pack(side=LEFT)
        ttk.Entry(short_box, textvariable=self.short_symbol, width=10).pack(side=LEFT, padx=5)
        ttk.Label(short_box, text=self.tr("qty")).pack(side=LEFT)
        ttk.Entry(short_box, textvariable=self.short_quantity, width=8).pack(side=LEFT, padx=5)
        short_button = ttk.Button(short_box, text=self.with_icon("▼", "short_sell"), command=self.short_sell)
        short_button.pack(side=LEFT, padx=5)
        self.add_tooltip(short_button, "tooltip_short")
        cover_button = ttk.Button(short_box, text=self.with_icon("▲", "cover_short"), command=self.cover_short)
        cover_button.pack(side=LEFT, padx=5)
        self.add_tooltip(cover_button, "tooltip_cover_short")
        ttk.Label(short_box, text=self.tr("insurance_symbol")).pack(side=LEFT, padx=(12, 0))
        ttk.Entry(short_box, textvariable=self.insurance_symbol, width=10).pack(side=LEFT, padx=5)
        insurance_button = ttk.Button(short_box, text=self.with_icon("◈", "buy_insurance"), command=self.buy_insurance)
        insurance_button.pack(side=LEFT, padx=5)
        self.add_tooltip(insurance_button, "tooltip_insurance")

        loans_box = ttk.Frame(parent)
        loans_box.grid(row=5, column=0, sticky="nsew")
        loans_box.columnconfigure(0, weight=1)
        loans_box.rowconfigure(1, weight=1)
        repayment = ttk.Frame(loans_box)
        repayment.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(repayment, text=self.tr("repayment_amount")).pack(side=LEFT)
        ttk.Entry(repayment, textvariable=self.bank_repayment, width=10).pack(side=LEFT, padx=6)
        repay_button = ttk.Button(repayment, text=self.with_icon("✓", "repay_selected"), command=self.repay_selected_bank_debt)
        repay_button.pack(side=LEFT)
        self.add_tooltip(repay_button, "tooltip_repay")
        ttk.Label(loans_box, text=self.tr("bank_header"), foreground=self.colors()["muted"]).grid(row=1, column=0, sticky="w", pady=(0, 4))
        self.bank_list = Listbox(loans_box, height=14, exportselection=False)
        self.configure_listbox(self.bank_list)
        self.bank_list.grid(row=2, column=0, sticky="nsew")
        loans_box.rowconfigure(2, weight=1)

    def build_orders_tab(self, parent) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)
        form = ttk.Frame(parent)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(form, text=self.tr("order_type")).pack(side=LEFT)
        ttk.Combobox(form, textvariable=self.order_type, values=["Limit Buy", "Limit Sell", "Stop Loss"], state="readonly", width=12).pack(side=LEFT, padx=6)
        ttk.Label(form, text=self.tr("symbol")).pack(side=LEFT)
        ttk.Entry(form, textvariable=self.order_symbol, width=10).pack(side=LEFT, padx=6)
        ttk.Label(form, text=self.tr("qty")).pack(side=LEFT)
        ttk.Entry(form, textvariable=self.order_quantity, width=8).pack(side=LEFT, padx=6)
        ttk.Label(form, text=self.tr("price")).pack(side=LEFT)
        ttk.Entry(form, textvariable=self.order_price, width=10).pack(side=LEFT, padx=6)
        place_button = ttk.Button(form, text=self.with_icon("＋", "place_order"), command=self.place_order)
        place_button.pack(side=LEFT, padx=8)
        self.add_tooltip(place_button, "tooltip_place_order")
        cancel_button = ttk.Button(form, text=self.with_icon("✕", "cancel_selected"), command=self.cancel_selected_order)
        cancel_button.pack(side=LEFT)
        self.add_tooltip(cancel_button, "tooltip_cancel_order")
        ttk.Label(parent, text=self.tr("order_help")).grid(row=1, column=0, sticky="w", pady=(0, 8))
        ttk.Label(parent, text=self.tr("orders_header"), foreground=self.colors()["muted"]).grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.orders_list = Listbox(parent, height=16, exportselection=False)
        self.configure_listbox(self.orders_list)
        self.orders_list.grid(row=3, column=0, sticky="nsew")

    def build_news_tab(self, parent) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        controls = ttk.Frame(parent)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(controls, text=self.tr("filter")).pack(side=LEFT)
        news_filter_box = ttk.Combobox(controls, textvariable=self.news_filter, values=["All", "Market", "Stock", "Crypto", "FNT", "Commodity", "Fund"], state="readonly", width=14)
        news_filter_box.pack(side=LEFT, padx=6)
        news_filter_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_news())
        news_refresh_button = ttk.Button(controls, text=self.with_icon("↻", "refresh"), command=self.refresh_news)
        news_refresh_button.pack(side=LEFT)
        self.add_tooltip(news_refresh_button, "tooltip_news_refresh")

        panes = ttk.PanedWindow(parent, orient="horizontal")
        panes.grid(row=1, column=0, sticky="nsew")
        feed_frame = ttk.Frame(panes, padding=8)
        detail_frame = ttk.Frame(panes, padding=8)
        panes.add(feed_frame, weight=2)
        panes.add(detail_frame, weight=3)

        feed_frame.rowconfigure(1, weight=1)
        feed_frame.columnconfigure(0, weight=1)
        ttk.Label(feed_frame, text=self.tr("news_feed"), font=("Arial", 16, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.news_list = Listbox(feed_frame, height=18, exportselection=False)
        self.configure_listbox(self.news_list)
        self.news_list.grid(row=1, column=0, sticky="nsew")
        news_scroll = ttk.Scrollbar(feed_frame, orient="vertical", command=self.news_list.yview)
        news_scroll.grid(row=1, column=1, sticky="ns")
        self.news_list.configure(yscrollcommand=news_scroll.set)
        self.news_list.bind("<<ListboxSelect>>", self.on_select_news)

        detail_frame.columnconfigure(0, weight=1)
        self.news_image = Canvas(detail_frame, height=160, background=self.colors()["bg"], highlightthickness=1, highlightbackground=self.colors()["border"])
        self.news_image.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.news_title = ttk.Label(detail_frame, text=self.tr("select_news_topic"), font=("Arial", 18, "bold"), wraplength=560)
        self.news_title.grid(row=1, column=0, sticky="ew")
        self.news_meta = ttk.Label(detail_frame, text="", foreground=self.colors()["muted"], wraplength=560)
        self.news_meta.grid(row=2, column=0, sticky="ew", pady=(4, 10))
        self.news_body = ttk.Label(detail_frame, text="", wraplength=560, justify=LEFT)
        self.news_body.grid(row=3, column=0, sticky="ew")
        self.news_insight = ttk.Label(detail_frame, text="", foreground=self.colors()["muted"], wraplength=560)
        self.news_insight.grid(row=4, column=0, sticky="ew", pady=(10, 8))
        self.news_select_button = ttk.Button(detail_frame, text=self.with_icon("↪", "open_asset"), command=self.select_news_asset)
        self.news_select_button.grid(row=5, column=0, sticky="w")
        self.add_tooltip(self.news_select_button, "tooltip_open_asset")

    def build_leaderboard_tab(self, parent) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        ttk.Label(parent, text=self.tr("local_leaderboard"), font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.leaderboard_list = Listbox(parent, height=18, exportselection=False)
        self.configure_listbox(self.leaderboard_list)
        self.leaderboard_list.grid(row=1, column=0, sticky="nsew")

    def build_settings_tab(self, parent) -> None:
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        colors = self.colors()
        canvas = Canvas(parent, background=colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)
        content = ttk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")
        content.columnconfigure(0, weight=1)

        def on_content_configure(_event=None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        def on_mousewheel(event) -> str:
            canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
            return "break"

        content.bind("<Configure>", on_content_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.bind("<MouseWheel>", on_mousewheel)
        content.bind("<MouseWheel>", on_mousewheel)
        canvas.bind("<Enter>", lambda _event: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda _event: canvas.unbind_all("<MouseWheel>"))

        account_box = ttk.LabelFrame(content, text=self.tr("account"), padding=14)
        account_box.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(account_box, text=f"{self.tr('username')}: {self.session.username}", font=("Arial", 12, "bold")).pack(anchor="w")
        ttk.Label(account_box, text=f"{self.tr('created')}: {self.session.user.get('created_at', 'Unknown')}").pack(anchor="w", pady=(4, 0))
        ttk.Label(account_box, text=f"{self.tr('trading_mode')}: {self.trading_mode_label(self.current_trading_mode())}").pack(anchor="w", pady=(4, 0))
        ttk.Label(account_box, text=f"{self.tr('last_closed')}: {self.session.user.get('last_closed_at') or self.tr('never')}").pack(anchor="w", pady=(4, 0))
        ttk.Label(account_box, text=f"{self.tr('last_login')}: {self.session.user.get('last_login_at') or self.tr('never')}").pack(anchor="w", pady=(4, 0))
        ttk.Button(account_box, text=self.with_icon("🔑", "change_password"), command=self.change_password).pack(anchor="w", pady=(10, 0))
        ttk.Button(account_box, text=self.with_icon("🗑", "delete_account"), command=self.delete_account).pack(anchor="w", pady=(4, 0))

        appearance_box = ttk.LabelFrame(content, text=self.tr("appearance"), padding=14)
        appearance_box.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        dark_mode_check = ttk.Checkbutton(appearance_box, text=self.with_icon("◐", "dark_mode"), variable=self.dark_mode, command=self.apply_settings_change)
        dark_mode_check.pack(anchor="w")
        self.add_tooltip(dark_mode_check, "tooltip_dark_mode")
        sound_check = ttk.Checkbutton(appearance_box, text=self.with_icon("♪", "sound_effects"), variable=self.sound_effects_enabled, command=self.apply_settings_change)
        sound_check.pack(anchor="w", pady=(6, 0))
        self.add_tooltip(sound_check, "tooltip_sound_effects")

        language_box = ttk.LabelFrame(content, text=self.tr("language"), padding=14)
        language_box.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        language_selector = ttk.Combobox(language_box, textvariable=self.language, values=LANGUAGES, state="readonly", width=22)
        language_selector.pack(anchor="w")
        language_selector.bind("<<ComboboxSelected>>", lambda _event: self.apply_settings_change())
        self.add_tooltip(language_selector, "tooltip_language")

        system_box = ttk.LabelFrame(content, text=self.tr("system"), padding=14)
        system_box.grid(row=3, column=0, sticky="ew")
        ttk.Label(
            system_box,
            text=self.tr("system_info", python=platform.python_version(), assets=len(self.get_assets())),
            foreground=self.colors()["muted"],
        ).pack(anchor="w")
        ttk.Label(system_box, text=f"Data: {DATA_DIR}", foreground=self.colors()["muted"]).pack(anchor="w", pady=(4, 0))

        simulation_box = ttk.LabelFrame(content, text=self.tr("simulation"), padding=14)
        simulation_box.grid(row=4, column=0, sticky="ew", pady=(12, 0))
        if self.show_speed_controls():
            ttk.Label(simulation_box, text=self.tr("speed_preset")).pack(anchor="w")
            ttk.Combobox(simulation_box, textvariable=self.speed_preset, values=["Slow", "Normal", "Fast", "Very Fast"], state="readonly", width=16).pack(anchor="w", pady=(2, 8))
        ttk.Label(simulation_box, text=self.tr("volatility_multiplier")).pack(anchor="w")
        ttk.Entry(simulation_box, textvariable=self.volatility_multiplier, width=10).pack(anchor="w", pady=(2, 8))
        ttk.Label(simulation_box, text=self.tr("event_frequency")).pack(anchor="w")
        ttk.Entry(simulation_box, textvariable=self.event_frequency, width=10).pack(anchor="w", pady=(2, 8))
        simulation_button = ttk.Button(simulation_box, text=self.with_icon("✓", "apply_simulation_settings"), command=self.apply_simulation_settings)
        simulation_button.pack(anchor="w")
        self.add_tooltip(simulation_button, "tooltip_simulation_settings")

        credits_box = ttk.LabelFrame(content, text=self.tr("credits"), padding=14)
        credits_box.grid(row=5, column=0, sticky="ew", pady=(12, 24))
        ttk.Label(credits_box, text=self.tr("credits_body"), wraplength=760, justify=LEFT, foreground=self.colors()["muted"]).pack(anchor="w")

    def apply_settings_change(self) -> None:
        was_live = self.live_updates_enabled
        self.save_user_preferences()
        self.apply_theme()
        self.status.set(self.tr("saved"))
        self.show_dashboard(start_live=was_live)

    def maybe_show_tutorial(self) -> None:
        settings = self.ensure_user_settings()
        if settings.get("tutorial_seen"):
            return
        settings["tutorial_seen"] = True
        self.session.save()
        messagebox.showinfo(
            self.tr("quick_start"),
            self.tr("quick_start_body"),
        )

    def apply_simulation_settings(self) -> None:
        presets = {"Slow": "8", "Normal": "3", "Fast": "1", "Very Fast": "0.5"}
        if self.show_speed_controls():
            self.live_interval_seconds.set(presets.get(self.speed_preset.get(), self.live_interval_seconds.get()))
        try:
            volatility = min(max(float(self.volatility_multiplier.get()), 0.2), 3.0)
            frequency = min(max(float(self.event_frequency.get()), 0.1), 5.0)
        except ValueError:
            messagebox.showerror("Invalid settings", "Use numeric values for volatility and event frequency.")
            return
        settings = self.session.market_data.setdefault("settings", {})
        settings["volatility_multiplier"] = volatility
        settings["event_frequency"] = frequency
        self.volatility_multiplier.set(f"{volatility:g}")
        self.event_frequency.set(f"{frequency:g}")
        if self.show_speed_controls():
            self.apply_live_speed()
        self.session.save()
        self.status.set("Simulation settings updated.")

    def change_password(self) -> None:
        current = simpledialog.askstring("Change Password", "Current password:", show="*")
        if current is None:
            return
        if not verify_password(current, self.session.user):
            messagebox.showerror("Password unchanged", "Current password is incorrect.")
            return
        new_password = simpledialog.askstring("Change Password", "New password:", show="*")
        if not new_password:
            return
        if len(new_password) < 4:
            messagebox.showerror("Password unchanged", "Use a password with at least 4 characters.")
            return
        salt, digest = hash_password(new_password)
        self.session.user["password_salt"] = salt
        self.session.user["password_hash"] = digest
        self.session.save()
        self.status.set("Password changed.")

    def delete_account(self) -> None:
        if not messagebox.askyesno("Delete Account", "Delete this account and return to the login screen? This cannot be undone."):
            return
        username = self.session.username
        self.stop_live_updates()
        self.session.users_data.get("users", {}).pop(username, None)
        self.session.save()
        self.session = None
        self.status.set("Account deleted.")
        self.show_login()

    def record_session_closed(self) -> None:
        if not self.session:
            return
        closed_ts, closed_at = self.now_stamp()
        self.session.user["last_closed_at"] = closed_at
        self.session.user["last_closed_at_ts"] = closed_ts
        self.session.save()

    def logout(self) -> None:
        self.record_session_closed()
        self.stop_live_updates()
        self.session = None
        self.status.set("Logged out.")
        self.show_login()

    def close_app(self) -> None:
        self.record_session_closed()
        self.stop_live_updates()
        self.root.destroy()

    def bind_shortcuts(self) -> None:
        self.root.bind("<Control-b>", lambda _event: self.buy_selected())
        self.root.bind("<Control-s>", lambda _event: self.sell_selected())
        self.root.bind("<Control-r>", lambda _event: self.refresh_all())
        self.root.bind("<Control-l>", lambda _event: self.logout())
        self.root.bind("<space>", lambda _event: self.toggle_live_updates() if self.show_manual_market_controls() else None)

    def get_assets(self) -> list[dict]:
        assert self.session is not None
        return self.session.market_data["assets"]

    def selected_asset(self) -> dict | None:
        symbol = self.selected_symbol.get()
        return next((item for item in self.get_assets() if item["symbol"] == symbol), None)

    def refresh_all(self) -> None:
        if not self.session:
            return
        self.process_bank_risk()
        self.record_net_worth_snapshot()
        self.session.save()
        self.refresh_account()
        self.refresh_market_list()
        self.refresh_portfolio()
        self.render_selected()
        self.refresh_transactions()
        self.refresh_performance()
        self.refresh_bank()
        self.refresh_orders()
        self.refresh_news()
        self.refresh_leaderboard()
        self.evaluate_achievements()
        self.refresh_achievements()
        self.refresh_dashboard()

    def portfolio_value(self, record: dict) -> float:
        holdings_value = 0.0
        for symbol, qty in record.get("portfolio", {}).items():
            found = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
            if found:
                holdings_value += found["price"] * qty
        return holdings_value

    def total_debt(self, record: dict) -> float:
        return round(self.total_bank_debt(record) + max(0.0, float(record.get("margin_debt", 0.0) or 0.0)), 2)

    def total_bank_debt(self, record: dict) -> float:
        return round(sum(max(0.0, loan.get("balance", 0.0)) for loan in record.get("loans", [])), 2)

    def total_short_liability(self, record: dict) -> float:
        liability = 0.0
        for symbol, position in record.get("short_positions", {}).items():
            item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
            if item:
                liability += item["price"] * position.get("quantity", 0)
        return round(liability, 2)

    def account_net_worth(self, record: dict) -> float:
        return record.get("cash", 0) + self.portfolio_value(record) - self.total_debt(record) - self.total_short_liability(record)

    def credit_limit(self, record: dict) -> float:
        score = min(max(int(record.get("credit_score", 650)), 300), 850)
        return round(CREDIT_LIMIT_BASE + score * CREDIT_LIMIT_SCORE_MULTIPLIER, 2)

    def used_credit(self, record: dict) -> float:
        return round(sum(max(0.0, loan.get("balance", 0.0)) for loan in record.get("loans", []) if loan.get("type") == "credit"), 2)

    def max_margin_available(self, record: dict) -> float:
        equity = max(0.0, record.get("cash", 0) + self.portfolio_value(record) - self.total_bank_debt(record) - self.total_short_liability(record))
        return round(max(0.0, equity * MARGIN_MAX_EQUITY_RATIO - float(record.get("margin_debt", 0.0) or 0.0)), 2)

    def leaderboard_rank(self, username: str | None = None) -> int | None:
        username = username or self.session.username
        rows = []
        for name, record in self.session.users_data.get("users", {}).items():
            rows.append((self.account_net_worth(record), name))
        for rank, (_net_worth, name) in enumerate(sorted(rows, reverse=True), start=1):
            if name == username:
                return rank
        return None

    def unlock_achievement(self, achievement_id: str, unlocked: list[str]) -> None:
        achievements = self.session.user.setdefault("achievements", {})
        if achievement_id in achievements:
            return
        achievements[achievement_id] = time.strftime("%Y-%m-%d %H:%M:%S")
        unlocked.append(achievement_id)

    def evaluate_achievements(self) -> None:
        if not self.session:
            return
        user = self.session.user
        unlocked: list[str] = []
        transactions = user.get("transactions", [])
        trade_actions = {"BUY", "SELL", "LIMIT BUY", "LIMIT SELL", "STOP LOSS"}
        category_holdings = {"Stock": 0, "Crypto": 0, "Fund": 0, "Commodity": 0, "FNT": 0}
        for symbol in user.get("portfolio", {}):
            item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
            if item:
                category = item.get("category", "Stock")
                category_holdings[category] = category_holdings.get(category, 0) + 1
        stats = {
            "trade_count": sum(1 for txn in transactions if txn.get("action") in trade_actions),
            "buy_count": sum(1 for txn in transactions if txn.get("action") in {"BUY", "LIMIT BUY"}),
            "sell_count": sum(1 for txn in transactions if txn.get("action") in {"SELL", "LIMIT SELL", "STOP LOSS"}),
            "portfolio_count": len(user.get("portfolio", {})),
            "net_worth": self.account_net_worth(user),
            "cash": user.get("cash", 0),
            "order_activity": len(user.get("orders", [])) + sum(1 for txn in transactions if txn.get("action") in {"LIMIT BUY", "LIMIT SELL", "STOP LOSS"}),
            "news_read_count": user.get("news_read_count", 0),
            "loan_count": sum(1 for txn in transactions if txn.get("action") in {"LOAN", "CREDIT"}),
            "repay_count": sum(1 for txn in transactions if txn.get("action") == "REPAY"),
            "debt": self.total_debt(user),
            "transaction_count": len(transactions),
            "stock_holdings": category_holdings.get("Stock", 0),
            "crypto_holdings": category_holdings.get("Crypto", 0),
            "fund_holdings": category_holdings.get("Fund", 0),
            "commodity_holdings": category_holdings.get("Commodity", 0),
            "fnt_holdings": category_holdings.get("FNT", 0),
        }
        if any(txn.get("action") in trade_actions for txn in transactions):
            self.unlock_achievement("first_trade", unlocked)
        if self.account_net_worth(user) > STARTING_CURRENCY:
            self.unlock_achievement("profit_start", unlocked)
        if len(user.get("portfolio", {})) >= 3:
            self.unlock_achievement("diversified", unlocked)
        if any(txn.get("action") in {"LOAN", "CREDIT"} for txn in transactions):
            self.unlock_achievement("borrower", unlocked)
        if any(txn.get("action") in {"LOAN", "CREDIT"} for txn in transactions) and self.total_debt(user) == 0:
            self.unlock_achievement("debt_free", unlocked)
        if len(user.get("orders", [])) >= 3 or sum(1 for txn in transactions if txn.get("action") in {"LIMIT BUY", "LIMIT SELL", "STOP LOSS"}) >= 3:
            self.unlock_achievement("order_master", unlocked)
        if user.get("news_read_count", 0) >= 5:
            self.unlock_achievement("market_reader", unlocked)
        if self.leaderboard_rank() == 1 and len(self.session.users_data.get("users", {})) > 1:
            self.unlock_achievement("local_leader", unlocked)
        for achievement_id, _title, _desc, metric, threshold in ADDITIONAL_ACHIEVEMENTS:
            if stats.get(metric, 0) >= threshold:
                self.unlock_achievement(achievement_id, unlocked)
        if unlocked:
            names = ", ".join(self.tr(next(title for ach_id, title, _desc in ACHIEVEMENTS if ach_id == achievement_id)) for achievement_id in unlocked)
            self.status.set(self.tr("achievement_unlocked", names=names))
            self.play_sound("achievement")
            self.flash_status("achievement")
            self.confetti_effect()
            self.session.save()

    def achievement_row(self, achievement_id: str, title_key: str, desc_key: str, unlocked_at: str | None = None) -> str:
        prefix = "★" if unlocked_at else "☆"
        suffix = f" ({unlocked_at})" if unlocked_at else ""
        return f"{prefix} {self.tr(title_key)} - {self.tr(desc_key)}{suffix}"

    def refresh_achievements(self) -> None:
        if not hasattr(self, "unlocked_achievements_list"):
            return
        self.unlocked_achievements_list.delete(0, END)
        self.locked_achievements_list.delete(0, END)
        achievements = self.session.user.setdefault("achievements", {})
        unlocked_count = 0
        locked_count = 0
        for achievement_id, title_key, desc_key in ACHIEVEMENTS:
            unlocked_at = achievements.get(achievement_id)
            if unlocked_at:
                self.unlocked_achievements_list.insert(END, self.achievement_row(achievement_id, title_key, desc_key, unlocked_at))
                unlocked_count += 1
            else:
                self.locked_achievements_list.insert(END, self.achievement_row(achievement_id, title_key, desc_key))
                locked_count += 1
        if not unlocked_count:
            self.unlocked_achievements_list.insert(END, self.tr("no_unlocked_achievements"))
        if not locked_count:
            self.locked_achievements_list.insert(END, self.tr("all_achievements_unlocked"))

    def market_change_percent(self, item: dict) -> float:
        history = item.get("history", [item.get("price", 0)])
        previous_price = history[-2] if len(history) > 1 else item.get("price", 0)
        return ((item.get("price", 0) - previous_price) / previous_price * 100) if previous_price else 0.0

    def refresh_dashboard(self) -> None:
        if not hasattr(self, "dashboard_summary"):
            return
        user = self.session.user
        holdings_value = self.portfolio_value(user)
        debt = self.total_debt(user)
        cash = user.get("cash", 0)
        net_worth = cash + holdings_value - debt
        portfolio_count = len(user.get("portfolio", {}))
        active_orders = len(user.get("orders", []))
        loans = len(user.get("loans", []))
        summary_lines = [
            f"{self.tr('cash')}: {money(cash)}",
            f"{self.tr('holdings')}: {money(holdings_value)} {self.tr('across_assets', count=portfolio_count)}",
            f"{self.tr('debt')}: {money(debt)} {self.tr('across_bank_items', count=loans)}",
            f"{self.tr('net_worth')}: {money(net_worth)}",
            f"{self.tr('orders')}: {self.tr('active_count', count=active_orders)}",
            f"{self.tr('trading_mode')}: {self.trading_mode_label(self.current_trading_mode())}",
        ]
        self.dashboard_summary.configure(text="\n".join(summary_lines))
        self.draw_allocation_chart(user)

        self.dashboard_movers.delete(0, END)
        movers = sorted(self.get_assets(), key=lambda item: abs(self.market_change_percent(item)), reverse=True)[:8]
        self.dashboard_mover_symbols = []
        if not movers:
            self.dashboard_movers.insert(END, self.tr("no_dashboard_items"))
        for item in movers:
            change = self.market_change_percent(item)
            self.dashboard_mover_symbols.append(item["symbol"])
            self.dashboard_movers.insert(END, f"{item['symbol']:<6} {change:+.2f}%  {item['name'][:28]:<28} {money(item['price'])}")
            self.dashboard_movers.itemconfig(self.dashboard_movers.size() - 1, foreground="#188038" if change >= 0 else "#d1242f")

        self.dashboard_news.delete(0, END)
        feed = [self.normalize_news_event(event) for event in reversed(self.session.market_data.get("news_feed", []))]
        if not feed:
            self.dashboard_news.insert(END, self.tr("no_matching_news"))
        for event in feed[:6]:
            warning = "!" if event.get("misleading") else " "
            self.dashboard_news.insert(END, f"{warning} {event.get('symbol', 'MARKET'):<6} {event.get('title', '')[:70]}")

        self.dashboard_alerts.delete(0, END)
        alerts = []
        if debt > 0:
            alerts.append(f"{self.tr('debt')}: {self.tr('outstanding_amount', amount=money(debt))}")
        if active_orders:
            alerts.append(f"{self.tr('orders')}: {self.tr('active_count', count=active_orders)}")
        misleading_count = sum(1 for event in feed[:12] if event.get("misleading"))
        if misleading_count:
            alerts.append(f"{self.tr('misleading_warning')}: {self.tr('recent_count', count=misleading_count)}")
        if not alerts:
            alerts.append(self.tr("no_risk_alerts"))
        for alert in alerts:
            self.dashboard_alerts.insert(END, alert)
        self.refresh_dashboard_news_quality(feed)
        self.refresh_dashboard_loan_due()

    def refresh_dashboard_news_quality(self, feed: list[dict]) -> None:
        if not hasattr(self, "dashboard_news_quality"):
            return
        self.dashboard_news_quality.delete(0, END)
        recent = feed[:20]
        if not recent:
            self.dashboard_news_quality.insert(END, self.tr("no_matching_news"))
            return
        avg_credibility = sum(event.get("credibility", 0.6) for event in recent) / len(recent)
        misleading = sum(1 for event in recent if event.get("misleading"))
        reliable = sum(1 for event in recent if event.get("credibility", 0.0) >= 0.7)
        self.dashboard_news_quality.insert(END, f"{self.tr('average_credibility')}: {avg_credibility * 100:.0f}%")
        self.dashboard_news_quality.insert(END, f"{self.tr('reliable_sources')}: {reliable}/{len(recent)}")
        self.dashboard_news_quality.insert(END, f"{self.tr('possible_hype')}: {misleading}/{len(recent)}")
        self.dashboard_news_quality.insert(END, self.tr("news_quality_hint"))

    def loan_due_date(self, loan: dict) -> tuple[str, int] | None:
        self.ensure_loan_terms(loan)
        due_ts = loan.get("due_at_ts")
        if not due_ts:
            return None
        days_left = int((due_ts - time.time()) // 86400)
        return time.strftime("%Y-%m-%d", time.localtime(due_ts)), days_left

    def refresh_dashboard_loan_due(self) -> None:
        if not hasattr(self, "dashboard_loan_due"):
            return
        self.dashboard_loan_due.delete(0, END)
        loans = self.session.user.get("loans", [])
        if not loans:
            self.dashboard_loan_due.insert(END, self.tr("no_bank_debt"))
            return
        for loan in loans[:6]:
            due = self.loan_due_date(loan)
            if due is None:
                due_label = self.tr("unknown_due")
            elif due[1] < 0:
                due_label = self.tr("overdue_by_days", date=due[0], days=abs(due[1]))
            else:
                due_label = self.tr("due_in_days", date=due[0], days=due[1])
            self.dashboard_loan_due.insert(
                END,
                f"{self.funding_type_label(loan.get('type', 'loan')):<10} {money(loan.get('balance', 0))}  {due_label}",
            )

    def open_dashboard_mover(self, _event=None) -> None:
        selection = self.dashboard_movers.curselection()
        symbols = getattr(self, "dashboard_mover_symbols", [])
        if not selection or selection[0] >= len(symbols):
            return
        self.select_asset_by_symbol(symbols[selection[0]])

    def draw_allocation_chart(self, user: dict) -> None:
        if not hasattr(self, "allocation_chart"):
            return
        chart = self.allocation_chart
        chart.delete("all")
        colors = self.colors()
        width = max(chart.winfo_width(), 420)
        height = 170
        chart.create_rectangle(0, 0, width, height, fill=colors["bg"], outline=colors["border"])
        holdings = []
        for symbol, qty in user.get("portfolio", {}).items():
            item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
            if item:
                holdings.append((symbol, qty * item["price"]))
        total = sum(value for _symbol, value in holdings)
        if total <= 0:
            chart.create_text(width / 2, height / 2, text=self.tr("no_allocation"), fill=colors["muted"], font=("Arial", 12, "bold"))
            return
        palette = ["#2563eb", "#16a34a", "#f97316", "#9333ea", "#dc2626", "#0891b2"]
        holdings = sorted(holdings, key=lambda row: row[1], reverse=True)
        top = holdings[:5]
        if len(holdings) > 5:
            top.append((self.tr("other"), sum(value for _symbol, value in holdings[5:])))
        start = 0.0
        box = (20, 24, 130, 134)
        for index, (symbol, value) in enumerate(top):
            extent = value / total * 359.9
            color = palette[index % len(palette)]
            chart.create_arc(*box, start=start, extent=extent, fill=color, outline=colors["bg"])
            y = 24 + index * 22
            chart.create_rectangle(160, y, 174, y + 14, fill=color, outline="")
            chart.create_text(182, y + 7, anchor="w", text=f"{symbol}: {value / total * 100:.1f}% ({money(value)})", fill=colors["text"], font=("Arial", 10))
            start += extent

    def refresh_account(self) -> None:
        user = self.session.user
        holdings_value = self.portfolio_value(user)
        debt = self.total_debt(user)
        self.account_label.configure(
            text=(
                f"{self.tr('username')}: {self.session.username}\n"
                f"{self.tr('cash')}: {money(user.get('cash', 0))}\n"
                f"{self.tr('holdings')}: {money(holdings_value)}\n"
                f"{self.tr('debt')}: {money(debt)}\n"
                f"{self.tr('net_worth')}: {money(user.get('cash', 0) + holdings_value - debt)}"
            )
        )

    def refresh_market_list(self) -> None:
        category = self.filter_var.get()
        previous = self.selected_symbol.get()
        self.market_list.delete(0, END)
        self.market_change_list.delete(0, END)
        self.visible_assets = []
        assets = list(self.get_assets())
        sort_key = self.sort_key_from_label(self.market_sort.get())
        if sort_key == "name":
            assets.sort(key=lambda item: item.get("name", ""))
        elif sort_key == "price":
            assets.sort(key=lambda item: item.get("price", 0), reverse=True)
        elif sort_key == "change":
            assets.sort(key=lambda item: self.market_change_percent(item), reverse=True)
        else:
            assets.sort(key=lambda item: item.get("symbol", ""))
        for item in assets:
            if category != "All" and item["category"] != category:
                continue
            self.visible_assets.append(item)
            history = item.get("history", [item["price"]])
            previous_price = history[-2] if len(history) > 1 else item["price"]
            change = ((item["price"] - previous_price) / previous_price * 100) if previous_price else 0
            self.market_list.insert(END, f"{item['symbol']:<6} {item['name'][:24]:<24} {money(item['price']):>11}")
            self.market_change_list.insert(END, f"{change:+.2f}%")
            color = "#188038" if change >= 0 else "#d1242f"
            self.market_change_list.itemconfig(self.market_change_list.size() - 1, foreground=color)
        if previous:
            for idx, item in enumerate(self.visible_assets):
                if item["symbol"] == previous:
                    self.market_list.selection_set(idx)
                    self.market_change_list.selection_set(idx)
                    self.market_list.see(idx)
                    self.market_change_list.see(idx)
                    break

    def refresh_portfolio(self) -> None:
        self.portfolio_list.delete(0, END)
        self.portfolio_symbols = []
        portfolio = self.session.user.get("portfolio", {})
        if not portfolio:
            self.portfolio_list.insert(END, self.tr("no_holdings"))
            return
        for symbol, qty in sorted(portfolio.items()):
            item = next((a for a in self.get_assets() if a["symbol"] == symbol), None)
            if item:
                self.portfolio_symbols.append(symbol)
                self.portfolio_list.insert(END, f"{symbol:<6} {qty:>8.3f} units   value {money(qty * item['price'])}")

    def refresh_transactions(self) -> None:
        if not hasattr(self, "transaction_list"):
            return
        self.transaction_list.delete(0, END)
        transactions = self.session.user.get("transactions", [])
        if not transactions:
            self.transaction_list.insert(END, self.tr("no_transactions"))
            return
        for txn in reversed(transactions[-150:]):
            total = txn.get("quantity", 0) * txn.get("price", 0)
            self.transaction_list.insert(
                END,
                f"{txn.get('time', '')}  {txn.get('action', ''):<10} {txn.get('symbol', ''):<6} "
                f"{txn.get('quantity', 0):>8.3f} @ {money(txn.get('price', 0))} = {money(total)}",
            )

    def refresh_bank(self) -> None:
        if not hasattr(self, "bank_list"):
            return
        user = self.session.user
        if hasattr(self, "bank_risk_summary"):
            self.bank_risk_summary.configure(
                text=(
                    f"{self.tr('credit_score')}: {user.get('credit_score', 650)} | "
                    f"{self.tr('credit_limit')}: {money(self.credit_limit(user))} | "
                    f"{self.tr('credit_used')}: {money(self.used_credit(user))} | "
                    f"{self.tr('margin_debt')}: {money(user.get('margin_debt', 0))} | "
                    f"{self.tr('short_liability')}: {money(self.total_short_liability(user))}"
                )
            )
        self.bank_list.delete(0, END)
        loans = user.get("loans", [])
        if not loans and not user.get("short_positions") and not user.get("insurance_policies") and not user.get("margin_debt", 0):
            self.bank_list.insert(END, self.tr("no_bank_debt"))
            return
        for loan in loans:
            due = loan.get("due_at", self.tr("unknown_due"))
            self.bank_list.insert(
                END,
                (
                    f"{loan.get('created_at', '')}  {self.funding_type_label(loan.get('type', 'loan')):<10} "
                    f"{self.tr('principal')} {money(loan.get('principal', 0))}  "
                    f"{self.tr('interest')} {loan.get('interest_rate', 0) * 100:.1f}%  "
                    f"{self.tr('minimum')} {money(loan.get('minimum_payment', 0))}  {self.tr('due')} {due}  "
                    f"{self.tr('balance')} {money(loan.get('balance', 0))}"
                ),
            )
        if user.get("margin_debt", 0):
            self.bank_list.insert(END, f"MARGIN      {self.tr('margin_debt')}: {money(user.get('margin_debt', 0))}  {self.tr('margin_available')}: {money(self.max_margin_available(user))}")
        for symbol, position in sorted(user.get("short_positions", {}).items()):
            item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
            current = item["price"] if item else position.get("entry_price", 0)
            liability = current * position.get("quantity", 0)
            self.bank_list.insert(END, f"SHORT       {symbol:<6} {self.tr('qty')} {position.get('quantity', 0):.3f} {self.tr('entry')} {money(position.get('entry_price', 0))} {self.tr('liability')} {money(liability)}")
        for policy in user.get("insurance_policies", []):
            self.bank_list.insert(END, f"{self.tr('hedge').upper():<11} {policy.get('symbol', ''):<6} {self.tr('floor')} {money(policy.get('floor_price', 0))} {self.tr('expires')} {policy.get('expires_at', '')}")

    def loan_terms(self, funding_type: str, amount: float, balance: float) -> dict:
        days = 7 if funding_type == "credit" else 14
        due_ts = time.time() + days * 86400
        return {
            "due_at": time.strftime("%Y-%m-%d", time.localtime(due_ts)),
            "due_at_ts": due_ts,
            "minimum_payment": round(max(1.0, balance * MINIMUM_PAYMENT_RATE), 2),
            "late_fee_applied": False,
            "defaulted": False,
        }

    def ensure_loan_terms(self, loan: dict) -> None:
        if "due_at_ts" in loan and "minimum_payment" in loan:
            return
        created_at = loan.get("created_at", "")
        try:
            created_ts = time.mktime(time.strptime(created_at, "%Y-%m-%d %H:%M:%S"))
        except (TypeError, ValueError):
            created_ts = time.time()
        days = 7 if loan.get("type") == "credit" else 14
        due_ts = created_ts + days * 86400
        loan.setdefault("due_at", time.strftime("%Y-%m-%d", time.localtime(due_ts)))
        loan.setdefault("due_at_ts", due_ts)
        loan.setdefault("minimum_payment", round(max(1.0, loan.get("balance", 0) * MINIMUM_PAYMENT_RATE), 2))
        loan.setdefault("late_fee_applied", False)
        loan.setdefault("defaulted", False)

    def adjust_credit_score(self, delta: int) -> None:
        user = self.session.user
        user["credit_score"] = min(850, max(300, int(user.get("credit_score", 650)) + delta))

    def process_bank_risk(self) -> None:
        if not self.session:
            return
        user = self.session.user
        changed = False
        now = time.time()
        for loan in user.get("loans", []):
            self.ensure_loan_terms(loan)
            overdue_days = int((now - loan.get("due_at_ts", now)) // 86400)
            if overdue_days >= 1 and not loan.get("late_fee_applied"):
                fee = round(max(2.0, loan.get("balance", 0) * LATE_FEE_RATE), 2)
                loan["balance"] = round(loan.get("balance", 0) + fee, 2)
                loan["late_fee_applied"] = True
                self.adjust_credit_score(-25)
                self.record_transaction("LATE FEE", "BANK", fee, 1)
                changed = True
            if overdue_days >= 7 and not loan.get("defaulted"):
                penalty = round(max(5.0, loan.get("balance", 0) * DEFAULT_PENALTY_RATE), 2)
                loan["balance"] = round(loan.get("balance", 0) + penalty, 2)
                loan["defaulted"] = True
                self.adjust_credit_score(-80)
                self.record_transaction("DEFAULT", "BANK", penalty, 1)
                changed = True
        changed = self.apply_insurance_payouts() or changed
        changed = self.enforce_liquidation_if_needed() or changed
        if changed:
            self.session.save()

    def apply_insurance_payouts(self) -> bool:
        user = self.session.user
        now = time.time()
        changed = False
        active_policies = []
        for policy in user.get("insurance_policies", []):
            if policy.get("expires_at_ts", now) < now:
                changed = True
                continue
            symbol = policy.get("symbol", "")
            item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
            held_qty = user.get("portfolio", {}).get(symbol, 0)
            covered_qty = min(float(policy.get("quantity", 0) or 0), held_qty)
            if item and covered_qty > 0 and item["price"] < policy.get("floor_price", 0):
                shortfall = (policy["floor_price"] - item["price"]) * covered_qty
                payout = round(shortfall * INSURANCE_PAYOUT_RATE, 2)
                if payout > 0:
                    user["cash"] = round(user.get("cash", 0) + payout, 2)
                    self.record_transaction("INSURANCE PAYOUT", symbol, covered_qty, payout / covered_qty)
                    self.status.set(self.tr("insurance_payout", symbol=symbol, amount=money(payout)))
                    self.trigger_effect("success", "HEDGE", "success")
                    changed = True
                continue
            active_policies.append(policy)
        if changed:
            user["insurance_policies"] = active_policies
        return changed

    def maintenance_requirement(self, record: dict) -> float:
        margin_requirement = float(record.get("margin_debt", 0.0) or 0.0) * MAINTENANCE_MARGIN_RATE
        short_requirement = self.total_short_liability(record) * SHORT_COLLATERAL_RATE
        return round(margin_requirement + short_requirement, 2)

    def enforce_liquidation_if_needed(self) -> bool:
        user = self.session.user
        if not user.get("margin_debt", 0) and not user.get("short_positions"):
            return False
        requirement = self.maintenance_requirement(user)
        if self.account_net_worth(user) >= requirement:
            return False

        changed = False
        assets_by_symbol = {item["symbol"]: item for item in self.get_assets()}
        holdings = sorted(
            user.get("portfolio", {}).items(),
            key=lambda row: assets_by_symbol.get(row[0], {}).get("price", 0) * row[1],
            reverse=True,
        )
        for symbol, qty in holdings:
            item = assets_by_symbol.get(symbol)
            if not item or qty <= 0:
                continue
            proceeds = round(qty * item["price"], 2)
            user["cash"] = round(user.get("cash", 0) + proceeds, 2)
            user.get("portfolio", {}).pop(symbol, None)
            self.record_transaction("LIQUIDATE", symbol, qty, item["price"])
            changed = True
            margin_debt = float(user.get("margin_debt", 0.0) or 0.0)
            if margin_debt > 0 and user.get("cash", 0) > 0:
                payment = min(user["cash"], margin_debt)
                user["cash"] = round(user["cash"] - payment, 2)
                user["margin_debt"] = round(margin_debt - payment, 2)
                self.record_transaction("MARGIN REPAY", "BANK", payment, 1)
            if self.account_net_worth(user) >= self.maintenance_requirement(user):
                break

        for symbol, position in list(user.get("short_positions", {}).items()):
            if self.account_net_worth(user) >= self.maintenance_requirement(user):
                break
            item = assets_by_symbol.get(symbol)
            if not item:
                continue
            quantity = float(position.get("quantity", 0.0) or 0.0)
            cost = round(quantity * item["price"], 2)
            if quantity <= 0 or cost > user.get("cash", 0):
                continue
            user["cash"] = round(user.get("cash", 0) - cost, 2)
            user["short_positions"].pop(symbol, None)
            self.record_transaction("FORCED COVER", symbol, quantity, item["price"])
            changed = True

        if changed:
            user.setdefault("liquidations", []).append(
                {
                    "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "net_worth": round(self.account_net_worth(user), 2),
                    "requirement": self.maintenance_requirement(user),
                }
            )
            del user["liquidations"][:-25]
            self.adjust_credit_score(-60)
            self.status.set(self.tr("liquidation_triggered"))
            self.trigger_effect("risk", "RISK", "risk")
        return changed

    def request_bank_funding(self) -> None:
        funding_type = self.funding_type_from_label(self.bank_funding_type.get())
        if funding_type not in LOAN_OPTIONS:
            funding_type = "loan"
        try:
            amount = float(self.bank_amount.get())
        except ValueError:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror(self.tr("bank_request_rejected"), self.tr("amount_must_be_numeric"))
            return
        if amount <= 0:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror(self.tr("bank_request_rejected"), self.tr("amount_must_be_positive"))
            return
        if amount > 1000:
            self.trigger_effect("error", "LIMIT", "error")
            messagebox.showerror(self.tr("bank_request_rejected"), self.tr("bank_amount_limit"))
            return
        option = LOAN_OPTIONS[funding_type]
        interest_rate = option["rate"]
        balance = round(amount * (1 + interest_rate), 2)
        user = self.session.user
        if funding_type == "credit" and self.used_credit(user) + balance > self.credit_limit(user):
            self.trigger_effect("error", "LIMIT", "error")
            messagebox.showerror(self.tr("bank_request_rejected"), self.tr("credit_limit_reached", limit=money(self.credit_limit(user))))
            return
        user["cash"] = round(user.get("cash", 0) + amount, 2)
        loan = {
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": funding_type,
            "principal": round(amount, 2),
            "interest_rate": interest_rate,
            "balance": balance,
        }
        loan.update(self.loan_terms(funding_type, amount, balance))
        user.setdefault("loans", []).append(loan)
        self.record_transaction(funding_type.upper(), "BANK", amount, 1)
        self.adjust_credit_score(3 if funding_type == "loan" else 1)
        self.status.set(self.tr("bank_funding_approved", amount=money(amount), balance=money(balance)))
        self.trigger_effect("success", "BANK", "success")
        self.refresh_all()

    def repay_selected_bank_debt(self) -> None:
        if not hasattr(self, "bank_list"):
            return
        selection = self.bank_list.curselection()
        loans = self.session.user.get("loans", [])
        if not selection or selection[0] >= len(loans):
            return
        try:
            amount = float(self.bank_repayment.get())
        except ValueError:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror(self.tr("repayment_rejected"), self.tr("amount_must_be_numeric"))
            return
        if amount <= 0:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror(self.tr("repayment_rejected"), self.tr("amount_must_be_positive"))
            return
        user = self.session.user
        if amount > user.get("cash", 0):
            self.trigger_effect("error", "CASH", "error")
            messagebox.showerror(self.tr("repayment_rejected"), self.tr("not_enough_cash_repay"))
            return
        loan = loans[selection[0]]
        payment = min(amount, loan.get("balance", 0))
        user["cash"] = round(user.get("cash", 0) - payment, 2)
        loan["balance"] = round(loan.get("balance", 0) - payment, 2)
        if loan["balance"] <= 0:
            loans.pop(selection[0])
            self.adjust_credit_score(20)
        elif payment >= loan.get("minimum_payment", 0):
            self.adjust_credit_score(5)
        self.record_transaction("REPAY", "BANK", payment, 1)
        self.status.set(self.tr("bank_repayment_recorded", amount=money(payment)))
        self.trigger_effect("success", "PAID", "success")
        self.refresh_all()

    def request_margin(self) -> None:
        try:
            amount = float(self.margin_amount.get())
        except ValueError:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror(self.tr("margin_rejected"), self.tr("amount_must_be_numeric"))
            return
        if amount <= 0:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror(self.tr("margin_rejected"), self.tr("amount_must_be_positive"))
            return
        user = self.session.user
        available = self.max_margin_available(user)
        if amount > available:
            self.trigger_effect("error", "LIMIT", "error")
            messagebox.showerror(self.tr("margin_rejected"), self.tr("margin_limit_reached", limit=money(available)))
            return
        user["cash"] = round(user.get("cash", 0) + amount, 2)
        user["margin_debt"] = round(float(user.get("margin_debt", 0.0) or 0.0) + amount, 2)
        self.record_transaction("MARGIN", "BANK", amount, 1)
        self.status.set(self.tr("margin_approved", amount=money(amount)))
        self.trigger_effect("risk", "MARGIN", "risk")
        self.refresh_all()

    def repay_margin(self) -> None:
        try:
            amount = float(self.margin_repayment.get())
        except ValueError:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror(self.tr("repayment_rejected"), self.tr("amount_must_be_numeric"))
            return
        user = self.session.user
        if amount <= 0:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror(self.tr("repayment_rejected"), self.tr("amount_must_be_positive"))
            return
        payment = min(amount, user.get("cash", 0), float(user.get("margin_debt", 0.0) or 0.0))
        if payment <= 0:
            return
        user["cash"] = round(user.get("cash", 0) - payment, 2)
        user["margin_debt"] = round(float(user.get("margin_debt", 0.0) or 0.0) - payment, 2)
        self.record_transaction("MARGIN REPAY", "BANK", payment, 1)
        self.status.set(self.tr("margin_repaid", amount=money(payment)))
        self.trigger_effect("success", "PAID", "success")
        self.refresh_all()

    def short_sell(self) -> None:
        symbol = (self.short_symbol.get().strip().upper() or self.selected_symbol.get())
        item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
        if not item:
            self.trigger_effect("error", "SYMBOL", "error")
            messagebox.showerror(self.tr("short_rejected"), self.tr("unknown_symbol"))
            return
        try:
            quantity = float(self.short_quantity.get())
        except ValueError:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror(self.tr("short_rejected"), self.tr("amount_must_be_numeric"))
            return
        if quantity <= 0:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror(self.tr("short_rejected"), self.tr("amount_must_be_positive"))
            return
        notional = item["price"] * quantity
        equity = self.account_net_worth(self.session.user)
        if equity < notional * SHORT_COLLATERAL_RATE:
            self.trigger_effect("error", "RISK", "error")
            messagebox.showerror(self.tr("short_rejected"), self.tr("short_collateral_needed", amount=money(notional * SHORT_COLLATERAL_RATE)))
            return
        position = self.session.user.setdefault("short_positions", {}).get(symbol, {"quantity": 0.0, "entry_price": item["price"]})
        total_qty = position.get("quantity", 0.0) + quantity
        avg_entry = ((position.get("entry_price", item["price"]) * position.get("quantity", 0.0)) + notional) / total_qty
        self.session.user["short_positions"][symbol] = {"quantity": round(total_qty, 3), "entry_price": round(avg_entry, 2)}
        self.session.user["cash"] = round(self.session.user.get("cash", 0) + notional, 2)
        self.record_transaction("SHORT", symbol, quantity, item["price"])
        self.status.set(self.tr("short_opened", symbol=symbol, amount=money(notional)))
        self.trigger_effect("risk", "SHORT", "risk")
        self.refresh_all()
        self.pulse_chart_latest("sell")

    def cover_short(self) -> None:
        symbol = (self.short_symbol.get().strip().upper() or self.selected_symbol.get())
        positions = self.session.user.setdefault("short_positions", {})
        position = positions.get(symbol)
        item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
        if not position or not item:
            return
        try:
            quantity = min(float(self.short_quantity.get()), position.get("quantity", 0.0))
        except ValueError:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror(self.tr("short_rejected"), self.tr("amount_must_be_numeric"))
            return
        cost = quantity * item["price"]
        if cost > self.session.user.get("cash", 0):
            self.trigger_effect("error", "CASH", "error")
            messagebox.showerror(self.tr("short_rejected"), self.tr("not_enough_cash_repay"))
            return
        self.session.user["cash"] = round(self.session.user.get("cash", 0) - cost, 2)
        remaining = round(position.get("quantity", 0.0) - quantity, 3)
        if remaining <= 0:
            positions.pop(symbol, None)
        else:
            position["quantity"] = remaining
        self.record_transaction("COVER", symbol, quantity, item["price"])
        self.status.set(self.tr("short_covered", symbol=symbol, amount=money(cost)))
        self.trigger_effect("success", "COVER", "success")
        self.refresh_all()
        self.pulse_chart_latest("trade")

    def buy_insurance(self) -> None:
        symbol = (self.insurance_symbol.get().strip().upper() or self.selected_symbol.get())
        item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
        qty = self.session.user.get("portfolio", {}).get(symbol, 0)
        if not item or qty <= 0:
            self.trigger_effect("error", "HOLD", "error")
            messagebox.showerror(self.tr("insurance_rejected"), self.tr("insurance_requires_holding"))
            return
        covered_value = item["price"] * qty
        premium = round(covered_value * INSURANCE_PREMIUM_RATE, 2)
        if premium > self.session.user.get("cash", 0):
            self.trigger_effect("error", "CASH", "error")
            messagebox.showerror(self.tr("insurance_rejected"), self.tr("not_enough_cash_repay"))
            return
        expires_ts = time.time() + 7 * 86400
        self.session.user["cash"] = round(self.session.user.get("cash", 0) - premium, 2)
        self.session.user.setdefault("insurance_policies", []).append({
            "symbol": symbol,
            "quantity": qty,
            "floor_price": round(item["price"] * 0.9, 2),
            "premium": premium,
            "expires_at": time.strftime("%Y-%m-%d", time.localtime(expires_ts)),
            "expires_at_ts": expires_ts,
        })
        self.record_transaction("INSURANCE", symbol, qty, premium / qty if qty else premium)
        self.status.set(self.tr("insurance_bought", symbol=symbol, amount=money(premium)))
        self.trigger_effect("success", "HEDGE", "success")
        self.refresh_all()

    def refresh_orders(self) -> None:
        if not hasattr(self, "orders_list"):
            return
        self.orders_list.delete(0, END)
        orders = self.session.user.get("orders", [])
        if not orders:
            self.orders_list.insert(END, self.tr("no_active_orders"))
            return
        for order in orders:
            self.orders_list.insert(
                END,
                f"{order.get('created_at', '')}  {order.get('type', ''):<10} {order.get('symbol', ''):<6} "
                f"{order.get('quantity', 0):>8.3f} target {money(order.get('target_price', 0))}",
            )

    def normalize_news_event(self, event: dict) -> dict:
        message = event.get("message", "")
        title = event.get("title") or message or self.tr("news")
        source = event.get("source") or "Market Desk"
        source_type = event.get("source_type") or "Newswire"
        credibility = event.get("credibility", 0.6)
        try:
            credibility = float(credibility)
        except (TypeError, ValueError):
            credibility = 0.6
        insight = event.get("insight") or self.tr("generic_news_insight")
        body = event.get("body") or f"{message}\n\n{self.tr('generic_news_body')}\n\n{self.tr('investment_insight')}: {insight}"
        return {
            **event,
            "title": title,
            "source": source,
            "source_type": source_type,
            "credibility": min(max(credibility, 0.0), 1.0),
            "impact": event.get("impact", "mixed"),
            "insight": insight,
            "body": body,
            "image_key": event.get("image_key") or "newspaper",
            "misleading": bool(event.get("misleading", False)),
        }

    def refresh_news(self) -> None:
        if not hasattr(self, "news_list"):
            return
        self.news_list.delete(0, END)
        news_filter = self.news_filter.get()
        feed = self.session.market_data.get("news_feed", [])
        self.visible_news = [self.normalize_news_event(event) for event in reversed(feed) if news_filter == "All" or event.get("category") == news_filter]
        if not self.visible_news:
            self.news_list.insert(END, self.tr("no_matching_news"))
            self.render_news_article(None)
            return
        self.visible_news = self.visible_news[:140]
        for event in self.visible_news:
            warning = " !" if event.get("misleading") else ""
            self.news_list.insert(END, f"{event.get('time', '')}  {event.get('symbol', ''):<6}  {event.get('title', '')}{warning}")
        self.news_list.selection_set(0)
        self.render_news_article(self.visible_news[0])

    def on_select_news(self, _event=None) -> None:
        selection = self.news_list.curselection()
        if not selection or selection[0] >= len(self.visible_news):
            return
        event = self.visible_news[selection[0]]
        self.mark_news_read(event)
        self.render_news_article(event)

    def news_event_id(self, event: dict) -> str:
        return f"{event.get('time', '')}|{event.get('symbol', '')}|{event.get('title', event.get('message', ''))}"

    def mark_news_read(self, event: dict) -> None:
        user = self.session.user
        read_news = user.setdefault("read_news", [])
        event_id = self.news_event_id(event)
        if event_id in read_news:
            return
        read_news.append(event_id)
        del read_news[:-200]
        user["news_read_count"] = int(user.get("news_read_count", 0)) + 1
        self.evaluate_achievements()
        self.refresh_achievements()
        self.refresh_dashboard()
        self.session.save()

    def render_news_article(self, event: dict | None) -> None:
        if not hasattr(self, "news_title"):
            return
        if not event:
            self.news_title.configure(text=self.tr("select_news_topic"))
            self.news_meta.configure(text="")
            self.news_body.configure(text="")
            self.news_insight.configure(text="")
            self.news_select_button.state(["disabled"])
            self.draw_news_image("empty", None)
            return
        credibility = event.get("credibility", 0.6) * 100
        risk = self.tr("misleading_warning") if event.get("misleading") else self.tr("credibility_note")
        meta = (
            f"{event.get('time', '')} | {event.get('source', '')} ({event.get('source_type', '')}) | "
            f"{self.tr('symbol')}: {event.get('symbol', 'MARKET')} | "
            f"{self.tr('credibility')}: {credibility:.0f}% | {risk}"
        )
        self.news_title.configure(text=event.get("title", ""))
        self.news_meta.configure(text=meta)
        self.news_body.configure(text=event.get("body", ""))
        self.news_insight.configure(text=f"{self.tr('investment_insight')}: {event.get('insight', '')}")
        symbol = event.get("symbol", "")
        if symbol and symbol != "MARKET" and any(item["symbol"] == symbol for item in self.get_assets()):
            self.news_select_button.state(["!disabled"])
        else:
            self.news_select_button.state(["disabled"])
        self.draw_news_image(event.get("image_key", "newspaper"), event)

    def select_news_asset(self) -> None:
        selection = self.news_list.curselection()
        if not selection or selection[0] >= len(self.visible_news):
            return
        symbol = self.visible_news[selection[0]].get("symbol", "")
        if symbol and symbol != "MARKET":
            self.select_asset_by_symbol(symbol)

    def draw_news_image(self, image_key: str, event: dict | None) -> None:
        canvas = self.news_image
        canvas.delete("all")
        colors = self.colors()
        width = max(canvas.winfo_width(), 560)
        height = 160
        canvas.create_rectangle(0, 0, width, height, fill=colors["bg"], outline=colors["border"])
        title = (event or {}).get("symbol", "VSM")
        if image_key == "youtuber":
            canvas.create_rectangle(18, 20, width - 18, height - 18, fill="#111827", outline="#ef4444", width=3)
            canvas.create_polygon(width / 2 - 22, 62, width / 2 - 22, 102, width / 2 + 20, 82, fill="#ef4444", outline="")
            canvas.create_text(40, 36, anchor="w", text="LIVE HYPE", fill="#fef2f2", font=("Arial", 18, "bold"))
            canvas.create_text(width - 36, 126, anchor="e", text=title, fill="#facc15", font=("Arial", 24, "bold"))
        elif image_key == "space":
            canvas.create_rectangle(0, 0, width, height, fill="#020617", outline="")
            for x, y in [(48, 34), (116, 76), (210, 28), (340, 52), (470, 30), (520, 96)]:
                canvas.create_oval(x, y, x + 3, y + 3, fill="#ffffff", outline="")
            canvas.create_oval(width - 118, 24, width - 34, 108, fill="#94a3b8", outline="#e2e8f0")
            canvas.create_polygon(92, 106, 122, 40, 152, 106, fill="#f8fafc", outline="#38bdf8", width=2)
            canvas.create_rectangle(112, 86, 132, 130, fill="#ef4444", outline="")
            canvas.create_text(24, 132, anchor="w", text="SPACE ECONOMY", fill="#bae6fd", font=("Arial", 18, "bold"))
        elif image_key == "oil":
            canvas.create_rectangle(0, 0, width, height, fill="#451a03", outline="")
            canvas.create_oval(50, 52, 150, 142, fill="#111827", outline="#f97316", width=4)
            canvas.create_polygon(100, 28, 84, 70, 116, 70, fill="#0f172a", outline="#f97316")
            canvas.create_line(210, 120, width - 70, 44, fill="#f97316", width=5)
            canvas.create_text(30, 34, anchor="w", text="SUPPLY SHOCK", fill="#fed7aa", font=("Arial", 20, "bold"))
            canvas.create_text(width - 34, 126, anchor="e", text="OIL WATCH", fill="#ffedd5", font=("Arial", 18, "bold"))
        elif image_key == "globe":
            canvas.create_rectangle(0, 0, width, height, fill="#0f172a", outline="")
            canvas.create_oval(40, 22, 176, 138, fill="#1d4ed8", outline="#93c5fd", width=3)
            canvas.create_arc(62, 30, 154, 132, start=70, extent=230, outline="#22c55e", width=6)
            canvas.create_line(230, 118, width - 40, 58, fill="#22c55e", width=4)
            canvas.create_line(230, 58, width - 40, 92, fill="#ef4444", width=4)
            canvas.create_text(220, 28, anchor="w", text="GLOBAL MACRO", fill="#dbeafe", font=("Arial", 20, "bold"))
        elif image_key == "empty":
            canvas.create_text(width / 2, height / 2, text=self.tr("select_news_topic"), fill=colors["muted"], font=("Arial", 16, "bold"))
        else:
            canvas.create_rectangle(24, 20, width - 24, height - 20, fill=colors["panel"], outline=colors["border"], width=2)
            canvas.create_text(48, 42, anchor="w", text="THE DAILY LEDGER", fill=colors["text"], font=("Arial", 18, "bold"))
            canvas.create_line(48, 62, width - 48, 62, fill=colors["border"], width=2)
            canvas.create_rectangle(48, 78, 188, 124, fill="#bfdbfe", outline="")
            canvas.create_line(216, 82, width - 54, 82, fill=colors["muted"], width=3)
            canvas.create_line(216, 102, width - 92, 102, fill=colors["muted"], width=3)
            canvas.create_line(216, 122, width - 144, 122, fill=colors["muted"], width=3)

    def refresh_leaderboard(self) -> None:
        if not hasattr(self, "leaderboard_list"):
            return
        self.leaderboard_list.delete(0, END)
        rows = []
        for username, record in self.session.users_data.get("users", {}).items():
            cash = record.get("cash", 0)
            holdings_value = self.portfolio_value(record)
            debt = self.total_debt(record)
            rows.append((cash + holdings_value - debt, username, cash, holdings_value, debt))
        for rank, (net_worth, username, cash, holdings_value, debt) in enumerate(sorted(rows, reverse=True), start=1):
            self.leaderboard_list.insert(END, f"#{rank:<3} {username:<18} net {money(net_worth):>12}  cash {money(cash):>12}  holdings {money(holdings_value):>12}  debt {money(debt):>12}")

    def record_net_worth_snapshot(self) -> None:
        user = self.session.user
        history = user.setdefault("net_worth_history", [])
        value = round(self.account_net_worth(user), 2)
        if not history or history[-1].get("value") != value:
            history.append({"time": time.strftime("%Y-%m-%d %H:%M:%S"), "value": value})
            del history[:-300]

    def refresh_performance(self) -> None:
        if not hasattr(self, "performance_chart"):
            return
        chart = self.performance_chart
        chart.delete("all")
        colors = self.colors()
        width = max(chart.winfo_width(), 620)
        height = 320
        pad = 34
        chart.create_rectangle(0, 0, width, height, fill=colors["bg"], outline=colors["border"])
        history = self.session.user.get("net_worth_history", [])
        if len(history) < 2:
            chart.create_text(width / 2, height / 2, text="More account changes are needed for a performance chart.", fill=colors["muted"])
            return
        values = [point["value"] for point in history[-120:]]
        low, high = min(values), max(values)
        if low == high:
            low -= 1
            high += 1
        chart.create_text(pad, pad, anchor="w", text=f"High {money(high)}", fill=colors["muted"])
        chart.create_text(pad, height - pad, anchor="w", text=f"Low {money(low)}", fill=colors["muted"])
        chart.create_line(pad, height - pad, width - pad, height - pad, fill=colors["border"])
        chart.create_line(pad, pad, pad, height - pad, fill=colors["border"])
        points = []
        for index, value in enumerate(values):
            x = pad + index * (width - pad * 2) / (len(values) - 1)
            y = height - pad - (value - low) * (height - pad * 2) / (high - low)
            points.extend([x, y])
        chart.create_line(*points, fill="#22c55e" if values[-1] >= values[0] else "#ef4444", width=3, smooth=True)

    def on_select_asset(self, _event=None) -> None:
        source = _event.widget if _event else self.market_list
        selection = source.curselection()
        if not selection:
            return
        self.market_list.selection_clear(0, END)
        self.market_change_list.selection_clear(0, END)
        self.market_list.selection_set(selection[0])
        self.market_change_list.selection_set(selection[0])
        asset_item = self.visible_assets[selection[0]]
        self.selected_symbol.set(asset_item["symbol"])
        self.order_symbol.set(asset_item["symbol"])
        self.render_selected()

    def scroll_market_lists(self, *args) -> None:
        self.market_list.yview(*args)
        self.market_change_list.yview(*args)

    def on_market_mousewheel(self, event):
        direction = -1 if event.delta > 0 else 1
        self.market_list.yview_scroll(direction, "units")
        self.market_change_list.yview_scroll(direction, "units")
        return "break"

    def on_portfolio_double_click(self, _event=None) -> None:
        selection = self.portfolio_list.curselection()
        if not selection or selection[0] >= len(self.portfolio_symbols):
            return
        self.select_asset_by_symbol(self.portfolio_symbols[selection[0]])

    def select_asset_by_symbol(self, symbol: str) -> None:
        item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
        if not item:
            return
        if self.filter_var.get() != "All" and self.filter_var.get() != item["category"]:
            self.filter_var.set("All")
        self.selected_symbol.set(symbol)
        self.refresh_market_list()
        self.render_selected()
        self.status.set(f"Selected {symbol} from your portfolio.")

    def place_order(self) -> None:
        symbol = self.order_symbol.get().strip().upper() or self.selected_symbol.get()
        item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
        if not item:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror("Order rejected", "Unknown symbol.")
            return
        try:
            quantity = float(self.order_quantity.get())
            target_price = float(self.order_price.get())
        except ValueError:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror("Order rejected", "Quantity and target price must be numeric.")
            return
        if quantity <= 0 or target_price <= 0:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror("Order rejected", "Quantity and target price must be greater than zero.")
            return
        order = {
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": self.order_type.get(),
            "symbol": symbol,
            "quantity": round(quantity, 3),
            "target_price": round(target_price, 2),
        }
        self.session.user.setdefault("orders", []).append(order)
        self.order_symbol.set(symbol)
        self.status.set(f"Placed {order['type']} for {symbol}.")
        self.trigger_effect("order", "ORDER", "order")
        self.refresh_all()

    def cancel_selected_order(self) -> None:
        if not hasattr(self, "orders_list"):
            return
        selection = self.orders_list.curselection()
        orders = self.session.user.get("orders", [])
        if not selection or selection[0] >= len(orders):
            return
        orders.pop(selection[0])
        self.status.set("Order cancelled.")
        self.trigger_effect("order", "CANCEL", "order")
        self.refresh_all()

    def process_orders(self) -> int:
        user = self.session.user
        remaining = []
        triggered = 0
        for order in user.get("orders", []):
            item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == order.get("symbol")), None)
            if not item:
                continue
            order_type = order.get("type")
            quantity = order.get("quantity", 0)
            target = order.get("target_price", 0)
            should_trigger = (
                (order_type == "Limit Buy" and item["price"] <= target)
                or (order_type == "Limit Sell" and item["price"] >= target)
                or (order_type == "Stop Loss" and item["price"] <= target)
            )
            if not should_trigger:
                remaining.append(order)
                continue
            if order_type == "Limit Buy":
                cost = item["price"] * quantity
                if cost <= user.get("cash", 0):
                    user["cash"] = round(user["cash"] - cost, 2)
                    user.setdefault("portfolio", {})[item["symbol"]] = round(user.get("portfolio", {}).get(item["symbol"], 0) + quantity, 3)
                    self.record_transaction("LIMIT BUY", item["symbol"], quantity, item["price"])
                    triggered += 1
                else:
                    remaining.append(order)
            else:
                owned = user.get("portfolio", {}).get(item["symbol"], 0)
                if owned >= quantity:
                    proceeds = item["price"] * quantity
                    user["cash"] = round(user["cash"] + proceeds, 2)
                    remaining_qty = round(owned - quantity, 3)
                    if remaining_qty <= 0:
                        user["portfolio"].pop(item["symbol"], None)
                    else:
                        user["portfolio"][item["symbol"]] = remaining_qty
                    self.record_transaction(order_type.upper(), item["symbol"], quantity, item["price"])
                    triggered += 1
                else:
                    remaining.append(order)
        user["orders"] = remaining
        if triggered:
            self.status.set(f"{triggered} order(s) triggered.")
            self.trigger_effect("order", f"{triggered} ORDER", "order")
        return triggered

    def render_selected(self) -> None:
        item = self.selected_asset()
        self.chart.delete("all")
        if not item:
            self.asset_title.configure(text=self.tr("select_asset"))
            self.asset_meta.configure(text="")
            self.event_log_label.configure(text="")
            return
        self.asset_title.configure(text=f"{item['symbol']} - {item['name']}")
        owned = self.session.user.get("portfolio", {}).get(item["symbol"], 0)
        self.asset_meta.configure(
            text=(
                f"{item['category']} | {item.get('sector', 'General')} | "
                f"Price {money(item['price'])} | Owned {owned:.3f} | "
                f"News: {item.get('news', 'Quiet trading')}"
            )
        )
        recent_events = item.get("event_log", [])[-3:]
        if recent_events:
            self.event_log_label.configure(text=self.tr("recent_events") + " | ".join(event["message"] for event in recent_events))
        else:
            self.event_log_label.configure(text=self.tr("recent_events_none"))
        full_history = item.get("history", [item["price"]])
        self.draw_chart(self.history_for_selected_range(full_history), len(full_history))

    def history_for_selected_range(self, history: list[float]) -> list[float]:
        limit = CHART_RANGES.get(self.chart_range.get())
        if limit is None:
            return history
        return history[-limit:]

    def draw_chart(self, history: list[float], total_points: int) -> None:
        width = max(self.chart.winfo_width(), 620)
        height = 260
        pad = 24
        self.chart_points = []
        colors = self.colors()
        self.chart.create_rectangle(0, 0, width, height, fill=colors["bg"], outline=colors["border"])
        if len(history) < 2:
            self.chart.create_text(width / 2, height / 2, text="More ticks needed for a chart", fill=colors["muted"])
            return
        low, high = min(history), max(history)
        if high == low:
            high += 1
            low -= 1
        for line in range(5):
            y = pad + line * (height - pad * 2) / 4
            value = high - line * (high - low) / 4
            self.chart.create_line(pad, y, width - pad, y, fill=colors["border"], dash=(2, 4))
            self.chart.create_text(pad + 4, y - 8, anchor="w", text=money(value), fill=colors["muted"], font=("Arial", 9))
        self.chart.create_line(pad, pad, pad, height - pad, fill=colors["border"])
        self.chart.create_line(pad, height - pad, width - pad, height - pad, fill=colors["border"])
        points = []
        for idx, price in enumerate(history):
            x = pad + idx * (width - pad * 2) / (len(history) - 1)
            y = height - pad - (price - low) * (height - pad * 2) / (high - low)
            points.extend([x, y])
            self.chart_points.append(
                {
                    "x": x,
                    "y": y,
                    "price": price,
                    "range_index": idx + 1,
                    "total_index": total_points - len(history) + idx + 1,
                    "range_total": len(history),
                    "total_points": total_points,
                }
            )
        color = "#188038" if history[-1] >= history[0] else "#d1242f"
        self.chart.create_line(*points, fill=color, width=3, smooth=True)
        self.chart.create_text(width - pad, pad, anchor="e", text=f"{self.chart_range.get()} view ({len(history)}/{total_points} ticks)", fill=colors["muted"])
        self.chart.create_text(pad, pad, anchor="w", text=f"High {money(high)}", fill=colors["muted"])
        self.chart.create_text(pad, height - pad, anchor="w", text=f"Low {money(low)}", fill=colors["muted"])

    def on_chart_click(self, event) -> None:
        if not self.chart_points:
            return
        nearest = min(
            self.chart_points,
            key=lambda point: abs(point["x"] - event.x) + abs(point["y"] - event.y) * 0.35,
        )
        self.draw_chart_marker(nearest)

    def draw_chart_marker(self, point: dict) -> None:
        self.chart.delete("chart_marker")
        width = max(self.chart.winfo_width(), 620)
        height = 260
        x = point["x"]
        y = point["y"]
        tooltip = (
            f"{money(point['price'])}\n"
            f"{self.chart_range.get()} point {point['range_index']}/{point['range_total']}\n"
            f"Market tick {point['total_index']}/{point['total_points']}"
        )

        colors = self.colors()
        self.chart.create_line(x, 24, x, height - 24, fill="#64748b", dash=(4, 3), tags="chart_marker")
        self.chart.create_line(24, y, width - 24, y, fill="#94a3b8", dash=(3, 5), tags="chart_marker")
        self.chart.create_oval(x - 6, y - 6, x + 6, y + 6, fill=colors["panel"], outline=colors["text"], width=2, tags="chart_marker")
        self.chart.create_oval(x - 2, y - 2, x + 2, y + 2, fill=colors["text"], outline=colors["text"], tags="chart_marker")

        box_width = 190
        box_height = 66
        box_x = min(max(x + 12, 28), width - box_width - 28)
        box_y = y - box_height - 12 if y > box_height + 44 else y + 16
        self.chart.create_rectangle(
            box_x + 3,
            box_y + 3,
            box_x + box_width + 3,
            box_y + box_height + 3,
            fill=colors["shadow"],
            outline="",
            tags="chart_marker",
        )
        self.chart.create_rectangle(
            box_x,
            box_y,
            box_x + box_width,
            box_y + box_height,
            fill=colors["panel"],
            outline=colors["text"],
            width=1,
            tags="chart_marker",
        )
        self.chart.create_text(box_x + 12, box_y + 12, anchor="nw", text=tooltip, fill=colors["text"], font=("Arial", 11), tags="chart_marker")

    def parse_quantity(self) -> float | None:
        try:
            qty = float(self.quantity.get())
        except ValueError:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror("Invalid quantity", "Enter a numeric quantity.")
            return None
        if qty <= 0:
            self.trigger_effect("error", "ERROR", "error")
            messagebox.showerror("Invalid quantity", "Quantity must be greater than zero.")
            return None
        return qty

    def buy_selected(self) -> None:
        item = self.selected_asset()
        qty = self.parse_quantity()
        if not item or qty is None:
            return
        cost = item["price"] * qty
        user = self.session.user
        if cost > user["cash"]:
            self.trigger_effect("error", "CASH", "error")
            messagebox.showerror("Not enough cash", f"Need {money(cost)}, but you have {money(user['cash'])}.")
            return
        user["cash"] = round(user["cash"] - cost, 2)
        user.setdefault("portfolio", {})[item["symbol"]] = round(user.get("portfolio", {}).get(item["symbol"], 0) + qty, 3)
        self.record_transaction("BUY", item["symbol"], qty, item["price"])
        self.status.set(f"Bought {qty:.3f} {item['symbol']} for {money(cost)}.")
        self.refresh_all()
        self.trigger_effect("trade", "BUY", "trade")
        self.pulse_chart_latest("trade")

    def sell_selected(self) -> None:
        item = self.selected_asset()
        qty = self.parse_quantity()
        if not item or qty is None:
            return
        user = self.session.user
        owned = user.get("portfolio", {}).get(item["symbol"], 0)
        if qty > owned:
            self.trigger_effect("error", "HOLD", "error")
            messagebox.showerror("Not enough holdings", f"You own {owned:.3f} {item['symbol']}.")
            return
        proceeds = item["price"] * qty
        user["cash"] = round(user["cash"] + proceeds, 2)
        remaining = round(owned - qty, 3)
        if remaining <= 0:
            user["portfolio"].pop(item["symbol"], None)
        else:
            user["portfolio"][item["symbol"]] = remaining
        self.record_transaction("SELL", item["symbol"], qty, item["price"])
        self.status.set(f"Sold {qty:.3f} {item['symbol']} for {money(proceeds)}.")
        self.refresh_all()
        self.trigger_effect("sell", "SELL", "sell")
        self.pulse_chart_latest("sell")

    def record_transaction(self, action: str, symbol: str, qty: float, price: float) -> None:
        self.session.user.setdefault("transactions", []).append(
            {
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "action": action,
                "symbol": symbol,
                "quantity": round(qty, 3),
                "price": round(price, 2),
            }
        )
        del self.session.user["transactions"][:-100]

    def process_dividends(self) -> None:
        user = self.session.user
        for symbol, qty in list(user.get("portfolio", {}).items()):
            item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
            if not item or item.get("category") not in {"Stock", "Fund"}:
                continue
            if time.time_ns() % 97 == 0:
                dividend = round(item["price"] * qty * 0.003, 2)
                if dividend > 0:
                    user["cash"] = round(user.get("cash", 0) + dividend, 2)
                    self.record_transaction("DIVIDEND", symbol, qty, dividend / qty if qty else dividend)
                    self.session.market_data.setdefault("news_feed", []).append(
                        {
                            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "symbol": symbol,
                            "category": item.get("category", "Stock"),
                            "message": f"{symbol} paid a small dividend to holders.",
                        }
                    )

    def tick(self) -> None:
        advance_market(self.session.market_data, ticks=1)
        self.process_dividends()
        triggered = self.process_orders()
        if triggered:
            self.status.set(f"Market tick simulated. {triggered} order(s) triggered.")
        else:
            self.status.set("Market tick simulated. Prices and news updated.")
        self.refresh_all()
        if not triggered:
            self.trigger_effect("trade", "TICK")
        self.pulse_chart_latest("trade")

    def start_live_updates(self) -> None:
        self.live_updates_enabled = True
        self.update_live_button_text()
        self.schedule_live_update()

    def stop_live_updates(self) -> None:
        self.live_updates_enabled = False
        self.update_live_button_text()
        if self.live_update_job:
            self.root.after_cancel(self.live_update_job)
            self.live_update_job = None

    def toggle_live_updates(self) -> None:
        if not self.show_manual_market_controls():
            return
        if self.live_updates_enabled:
            self.stop_live_updates()
            self.status.set("Market updates frozen. Manual ticks still work.")
            self.trigger_effect("order", "PAUSE", "order")
        else:
            self.start_live_updates()
            self.status.set(f"Market updates resumed at {self.current_interval_seconds():.1f}s per tick.")
            self.trigger_effect("success", "LIVE", "success")

    def apply_live_speed(self) -> None:
        if not self.show_speed_controls():
            self.live_interval_seconds.set("1")
            return
        interval = self.current_interval_seconds()
        self.live_interval_seconds.set(f"{interval:g}")
        if self.session:
            settings = self.ensure_user_settings()
            settings["live_interval_seconds"] = interval
        if self.live_updates_enabled:
            if self.live_update_job:
                self.root.after_cancel(self.live_update_job)
                self.live_update_job = None
            self.schedule_live_update()
        self.status.set(f"Market step speed set to {interval:.1f} seconds.")
        self.trigger_effect("success", "SPEED", "success")

    def current_interval_seconds(self, show_errors: bool = True) -> float:
        if self.current_trading_mode() == "realistic":
            return 1.0
        try:
            interval = float(self.live_interval_seconds.get())
        except ValueError:
            if show_errors:
                messagebox.showerror("Invalid speed", "Enter a number of seconds between 0.5 and 60.")
            return 3.0
        if interval < 0.5:
            interval = 0.5
        if interval > 60:
            interval = 60.0
        return interval

    def schedule_live_update(self) -> None:
        if not self.live_updates_enabled or not self.session:
            return
        delay_ms = int(self.current_interval_seconds() * 1000)
        self.live_update_job = self.root.after(delay_ms, self.live_update)

    def live_update(self) -> None:
        self.live_update_job = None
        if not self.live_updates_enabled or not self.session:
            return
        advance_market(self.session.market_data, ticks=1)
        self.process_dividends()
        triggered = self.process_orders()
        if triggered:
            self.status.set(f"Live tick triggered {triggered} order(s). Next update in {self.current_interval_seconds():.1f}s.")
        else:
            self.status.set(f"Live market tick. Next update in {self.current_interval_seconds():.1f}s.")
        self.refresh_all()
        if triggered:
            self.pulse_chart_latest("trade")
        self.schedule_live_update()
