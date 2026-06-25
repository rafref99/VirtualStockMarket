from __future__ import annotations

import platform
import random
import time
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, X, Y, BooleanVar, Canvas, Label, Listbox, StringVar, Tk, Toplevel, filedialog, messagebox, simpledialog
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
NEWS_VIEWS = ("all", "unread", "bookmarked")
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
        self.news_search = StringVar(value="")
        self.news_view = StringVar(value="")
        self.order_type = StringVar(value="Limit Buy")
        self.order_symbol = StringVar()
        self.order_quantity = StringVar(value="1")
        self.order_price = StringVar(value="10")
        self.bank_funding_type = StringVar(value="")
        self.bank_amount = StringVar(value="25")
        self.bank_repayment = StringVar(value="25")
        self.bank_advanced_visible = BooleanVar(value=False)
        self.margin_amount = StringVar(value="25")
        self.margin_repayment = StringVar(value="25")
        self.short_symbol = StringVar()
        self.short_quantity = StringVar(value="1")
        self.insurance_symbol = StringVar()
        self.language = StringVar(value="English")
        self.dark_mode = BooleanVar(value=False)
        self.live_button_text = StringVar(value="")
        self.chart_range = StringVar(value="Days")
        self.chart_points: list[dict] = []
        self.portfolio_symbols: list[str] = []
        self.visible_news: list[dict] = []
        self.selected_news_id = ""
        self.last_breaking_news_id = ""
        self.refreshing_market_list = False
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

    def news_view_label(self, view: str) -> str:
        return self.tr(f"news_view_{view}") if view in NEWS_VIEWS else self.tr("news_view_all")

    def news_view_from_label(self, label: str) -> str:
        for view in NEWS_VIEWS:
            if label == self.news_view_label(view):
                return view
        return "all"

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

    def trigger_effect(self, kind: str = "success", label: str = "") -> None:
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
        settings.pop("sound_effects_enabled", None)
        settings.setdefault("trading_mode", "sandbox")
        settings.setdefault("live_interval_seconds", 3.0)
        return settings

    def load_user_preferences(self) -> None:
        settings = self.ensure_user_settings()
        language = settings.get("language", "English")
        self.language.set(language if language in LANGUAGES else "English")
        self.dark_mode.set(bool(settings.get("dark_mode", False)))
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

    def compressed_offline_ticks(self, raw_ticks: int) -> int:
        if raw_ticks <= 300:
            return max(0, raw_ticks)
        compressed = 300 + int((raw_ticks - 300) ** 0.5 * 20)
        return min(compressed, 1200)

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
            ticks = self.compressed_offline_ticks(int(elapsed // interval))
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
        self.asset_meta = ttk.Label(detail, text="", wraplength=620)
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

        self.last_breaking_news_id = self.latest_breaking_news_id()
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
        parent.rowconfigure(4, weight=1)
        self.bank_funding_type.set(self.funding_type_label("loan"))
        ttk.Label(parent, text=self.tr("bank"), font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))

        overview = ttk.LabelFrame(parent, text=self.tr("bank_overview"), padding=12)
        overview.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        for column in range(4):
            overview.columnconfigure(column, weight=1)
        ttk.Label(overview, text=self.tr("cash"), foreground=self.colors()["muted"]).grid(row=0, column=0, sticky="w")
        self.bank_cash_value = ttk.Label(overview, text="", font=("Arial", 12, "bold"))
        self.bank_cash_value.grid(row=1, column=0, sticky="w", pady=(2, 0))
        ttk.Label(overview, text=self.tr("debt"), foreground=self.colors()["muted"]).grid(row=0, column=1, sticky="w")
        self.bank_debt_value = ttk.Label(overview, text="", font=("Arial", 12, "bold"))
        self.bank_debt_value.grid(row=1, column=1, sticky="w", pady=(2, 0))
        ttk.Label(overview, text=self.tr("next_payment"), foreground=self.colors()["muted"]).grid(row=0, column=2, sticky="w")
        self.bank_next_payment_value = ttk.Label(overview, text="", font=("Arial", 12, "bold"), wraplength=250)
        self.bank_next_payment_value.grid(row=1, column=2, sticky="w", pady=(2, 0))
        ttk.Label(overview, text=self.tr("credit_available"), foreground=self.colors()["muted"]).grid(row=0, column=3, sticky="w")
        self.bank_credit_value = ttk.Label(overview, text="", font=("Arial", 12, "bold"))
        self.bank_credit_value.grid(row=1, column=3, sticky="w", pady=(2, 0))

        actions = ttk.Frame(parent)
        actions.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)

        funding_box = ttk.LabelFrame(actions, text=self.tr("quick_funding"), padding=14)
        funding_box.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        funding_box.columnconfigure(1, weight=1)
        ttk.Label(funding_box, text=self.tr("quick_funding_help"), foreground=self.colors()["muted"], wraplength=340).grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        ttk.Label(funding_box, text=self.tr("amount")).grid(row=1, column=0, sticky="w")
        ttk.Entry(funding_box, textvariable=self.bank_amount, width=12).grid(row=1, column=1, sticky="ew", padx=6)
        request_button = ttk.Button(funding_box, text=self.with_icon("＋", "get_cash"), command=self.request_simple_bank_funding)
        request_button.grid(row=1, column=2, sticky="e")
        self.add_tooltip(request_button, "tooltip_bank_request")

        payment_box = ttk.LabelFrame(actions, text=self.tr("automatic_repayment"), padding=14)
        payment_box.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        payment_box.columnconfigure(0, weight=1)
        self.bank_next_payment_detail = ttk.Label(payment_box, text="", foreground=self.colors()["muted"], wraplength=340)
        self.bank_next_payment_detail.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        pay_next_button = ttk.Button(payment_box, text=self.with_icon("✓", "pay_next_due"), command=self.repay_next_bank_debt)
        pay_next_button.grid(row=1, column=0, sticky="w")
        self.add_tooltip(pay_next_button, "tooltip_pay_next_due")

        ttk.Label(parent, text=self.tr("debt_schedule"), font=("Arial", 13, "bold")).grid(row=3, column=0, sticky="w", pady=(0, 4))
        loans_box = ttk.Frame(parent)
        loans_box.grid(row=4, column=0, sticky="nsew")
        loans_box.columnconfigure(0, weight=1)
        loans_box.rowconfigure(1, weight=1)
        ttk.Label(loans_box, text=self.tr("debt_schedule_header"), foreground=self.colors()["muted"]).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.bank_list = Listbox(loans_box, height=10, exportselection=False)
        self.configure_listbox(self.bank_list)
        self.bank_list.grid(row=1, column=0, sticky="nsew")

        self.bank_advanced_button = ttk.Button(parent, command=self.toggle_bank_advanced_tools)
        self.bank_advanced_button.grid(row=5, column=0, sticky="w", pady=(12, 8))
        self.update_bank_advanced_button()

        self.bank_advanced_frame = ttk.LabelFrame(parent, text=self.tr("advanced_bank_tools"), padding=14)
        self.bank_advanced_frame.grid(row=6, column=0, sticky="ew")
        self.bank_advanced_frame.columnconfigure(0, weight=1)
        self.bank_risk_summary = ttk.Label(self.bank_advanced_frame, text="", foreground=self.colors()["muted"], wraplength=900)
        self.bank_risk_summary.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        advanced_funding = ttk.Frame(self.bank_advanced_frame)
        advanced_funding.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(advanced_funding, text=self.tr("advanced_funding")).pack(side=LEFT)
        ttk.Combobox(
            advanced_funding,
            textvariable=self.bank_funding_type,
            values=[self.funding_type_label(funding_type) for funding_type in LOAN_OPTIONS],
            state="readonly",
            width=10,
        ).pack(side=LEFT, padx=6)
        ttk.Label(advanced_funding, text=self.tr("amount")).pack(side=LEFT)
        ttk.Entry(advanced_funding, textvariable=self.bank_amount, width=10).pack(side=LEFT, padx=6)
        advanced_request_button = ttk.Button(advanced_funding, text=self.with_icon("＋", "request"), command=self.request_bank_funding)
        advanced_request_button.pack(side=LEFT, padx=6)
        self.add_tooltip(advanced_request_button, "tooltip_bank_request")
        ttk.Label(advanced_funding, text=self.tr("bank_help"), foreground=self.colors()["muted"]).pack(side=LEFT, padx=10)

        repayment = ttk.Frame(self.bank_advanced_frame)
        repayment.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(repayment, text=self.tr("custom_repayment")).pack(side=LEFT)
        ttk.Entry(repayment, textvariable=self.bank_repayment, width=10).pack(side=LEFT, padx=6)
        repay_button = ttk.Button(repayment, text=self.with_icon("✓", "repay_selected"), command=self.repay_selected_bank_debt)
        repay_button.pack(side=LEFT)
        self.add_tooltip(repay_button, "tooltip_repay")

        risk_box = ttk.Frame(self.bank_advanced_frame)
        risk_box.grid(row=3, column=0, sticky="ew", pady=(0, 10))
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

        short_box = ttk.Frame(self.bank_advanced_frame)
        short_box.grid(row=4, column=0, sticky="ew", pady=(0, 10))
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

        ttk.Label(self.bank_advanced_frame, text=self.tr("risk_positions"), foreground=self.colors()["muted"]).grid(row=5, column=0, sticky="w", pady=(0, 4))
        self.bank_risk_list = Listbox(self.bank_advanced_frame, height=5, exportselection=False)
        self.configure_listbox(self.bank_risk_list)
        self.bank_risk_list.grid(row=6, column=0, sticky="ew")
        if not self.bank_advanced_visible.get():
            self.bank_advanced_frame.grid_remove()

    def update_bank_advanced_button(self) -> None:
        if not hasattr(self, "bank_advanced_button"):
            return
        if self.bank_advanced_visible.get():
            self.bank_advanced_button.configure(text=self.with_icon("▾", "hide_advanced"))
        else:
            self.bank_advanced_button.configure(text=self.with_icon("▸", "show_advanced"))

    def toggle_bank_advanced_tools(self) -> None:
        self.bank_advanced_visible.set(not self.bank_advanced_visible.get())
        if hasattr(self, "bank_advanced_frame"):
            if self.bank_advanced_visible.get():
                self.bank_advanced_frame.grid()
            else:
                self.bank_advanced_frame.grid_remove()
        self.update_bank_advanced_button()

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
        controls.columnconfigure(3, weight=1)
        ttk.Label(controls, text=self.tr("filter")).pack(side=LEFT)
        news_filter_box = ttk.Combobox(controls, textvariable=self.news_filter, values=["All", "Market", "Stock", "Crypto", "FNT", "Commodity", "Fund"], state="readonly", width=14)
        news_filter_box.pack(side=LEFT, padx=6)
        news_filter_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_news())
        ttk.Label(controls, text=self.tr("view")).pack(side=LEFT, padx=(10, 4))
        current_view = self.news_view_from_label(self.news_view.get())
        self.news_view.set(self.news_view_label(current_view))
        news_view_box = ttk.Combobox(controls, textvariable=self.news_view, values=[self.news_view_label(view) for view in NEWS_VIEWS], state="readonly", width=14)
        news_view_box.pack(side=LEFT, padx=6)
        news_view_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_news())
        ttk.Label(controls, text=self.tr("search")).pack(side=LEFT, padx=(10, 4))
        news_search_entry = ttk.Entry(controls, textvariable=self.news_search, width=22)
        news_search_entry.pack(side=LEFT, padx=6)
        news_search_entry.bind("<Return>", lambda _event: self.refresh_news())
        search_button = ttk.Button(controls, text=self.with_icon("⌕", "search"), command=self.refresh_news)
        search_button.pack(side=LEFT)
        clear_button = ttk.Button(controls, text=self.tr("clear"), command=self.clear_news_search)
        clear_button.pack(side=LEFT, padx=(4, 0))
        news_refresh_button = ttk.Button(controls, text=self.with_icon("↻", "refresh"), command=self.refresh_news)
        news_refresh_button.pack(side=LEFT, padx=(4, 0))
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
        self.news_source_reputation = ttk.Label(detail_frame, text="", foreground=self.colors()["muted"], wraplength=560)
        self.news_source_reputation.grid(row=5, column=0, sticky="ew", pady=(0, 6))
        self.news_impact_timeline = ttk.Label(detail_frame, text="", foreground=self.colors()["muted"], wraplength=560)
        self.news_impact_timeline.grid(row=6, column=0, sticky="ew", pady=(0, 8))
        news_actions = ttk.Frame(detail_frame)
        news_actions.grid(row=7, column=0, sticky="w")
        self.news_select_button = ttk.Button(news_actions, text=self.with_icon("↪", "open_asset"), command=self.select_news_asset)
        self.news_select_button.pack(side=LEFT)
        self.add_tooltip(self.news_select_button, "tooltip_open_asset")
        self.news_bookmark_button = ttk.Button(news_actions, text=self.with_icon("★", "bookmark"), command=self.toggle_news_bookmark)
        self.news_bookmark_button.pack(side=LEFT, padx=(6, 0))
        self.news_unread_button = ttk.Button(news_actions, text=self.with_icon("•", "mark_unread"), command=self.mark_selected_news_unread)
        self.news_unread_button.pack(side=LEFT, padx=(6, 0))

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

        data_box = ttk.LabelFrame(content, text=self.tr("data_management"), padding=14)
        data_box.grid(row=4, column=0, sticky="ew", pady=(12, 0))
        ttk.Label(data_box, text=self.tr("data_management_help"), wraplength=760, foreground=self.colors()["muted"]).pack(anchor="w", pady=(0, 8))
        data_actions = ttk.Frame(data_box)
        data_actions.pack(anchor="w", fill=X)
        ttk.Button(data_actions, text=self.with_icon("⇧", "export_save"), command=self.export_save_file).pack(side=LEFT, padx=(0, 6))
        ttk.Button(data_actions, text=self.with_icon("⇩", "import_save"), command=self.import_save_file).pack(side=LEFT, padx=6)
        ttk.Button(data_actions, text=self.with_icon("↻", "reset_market"), command=self.reset_market_data).pack(side=LEFT, padx=6)
        ttk.Button(data_actions, text=self.with_icon("⌫", "reset_account_progress"), command=self.reset_account_progress).pack(side=LEFT, padx=6)

        simulation_box = ttk.LabelFrame(content, text=self.tr("simulation"), padding=14)
        simulation_box.grid(row=5, column=0, sticky="ew", pady=(12, 0))
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
        credits_box.grid(row=6, column=0, sticky="ew", pady=(12, 24))
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

    def export_save_file(self) -> None:
        default_name = f"virtual_stock_market_save_{time.strftime('%Y%m%d_%H%M%S')}.json"
        path = filedialog.asksaveasfilename(
            title=self.tr("export_save"),
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        self.session.save()
        package = {
            "format": "VirtualStockMarketSave",
            "version": 1,
            "exported_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "users": load_json(USERS_FILE, {"users": {}}),
            "market": load_json(MARKET_FILE, {"last_tick": time.time(), "assets": generate_market()}),
            "app_settings": load_json(APP_SETTINGS_FILE, {"remembered_username": ""}),
        }
        try:
            save_json(Path(path), package)
        except OSError as exc:
            messagebox.showerror(self.tr("export_failed"), str(exc))
            return
        self.status.set(self.tr("export_complete"))

    def import_save_file(self) -> None:
        path = filedialog.askopenfilename(
            title=self.tr("import_save"),
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        package = load_json(Path(path), {})
        if package.get("format") != "VirtualStockMarketSave" or not isinstance(package.get("users"), dict) or not isinstance(package.get("market"), dict):
            messagebox.showerror(self.tr("import_failed"), self.tr("invalid_save_file"))
            return
        if not messagebox.askyesno(self.tr("import_save"), self.tr("confirm_import_save")):
            return
        self.stop_live_updates()
        users = normalize_users_data(package.get("users", {"users": {}}))
        market = normalize_market_data(package.get("market", {"last_tick": time.time(), "assets": generate_market()}))
        app_settings = package.get("app_settings", {"remembered_username": ""})
        if not isinstance(app_settings, dict):
            app_settings = {"remembered_username": ""}
        try:
            save_json(USERS_FILE, users)
            save_json(MARKET_FILE, market)
            save_json(APP_SETTINGS_FILE, app_settings)
        except OSError as exc:
            messagebox.showerror(self.tr("import_failed"), str(exc))
            return
        username = self.session.username if self.session else ""
        if username and username in users.get("users", {}):
            self.session = self.load_session(username)
            self.load_user_preferences()
            self.status.set(self.tr("import_complete"))
            self.show_dashboard()
        else:
            self.session = None
            self.status.set(self.tr("import_complete_login"))
            self.show_login()

    def reset_market_data(self) -> None:
        if not messagebox.askyesno(self.tr("reset_market"), self.tr("confirm_reset_market")):
            return
        self.stop_live_updates()
        settings = {}
        if self.session:
            settings = dict(self.session.market_data.get("settings", {}))
        market = normalize_market_data({"last_tick": time.time(), "assets": generate_market(), "settings": settings})
        save_json(MARKET_FILE, market)
        if self.session:
            self.session.market_data = market
            self.status.set(self.tr("market_reset_complete"))
            self.show_dashboard()
        else:
            self.status.set(self.tr("market_reset_complete"))

    def reset_account_progress(self) -> None:
        if not self.session:
            return
        if not messagebox.askyesno(self.tr("reset_account_progress"), self.tr("confirm_reset_account_progress")):
            return
        user = self.session.user
        user["cash"] = STARTING_CURRENCY
        user["portfolio"] = {}
        user["transactions"] = []
        user["orders"] = []
        user["loans"] = []
        user["credit_score"] = 650
        user["margin_debt"] = 0.0
        user["short_positions"] = {}
        user["insurance_policies"] = []
        user["liquidations"] = []
        user["achievements"] = {}
        user["read_news"] = []
        user["bookmarked_news"] = []
        user["news_read_count"] = 0
        user["net_worth_history"] = []
        user["last_offline_summary"] = {}
        self.selected_symbol.set("")
        self.selected_news_id = ""
        self.session.save()
        self.status.set(self.tr("account_progress_reset_complete"))
        self.show_dashboard()

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
        self.process_daily_quests()
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

    def daily_quest_stats(self) -> dict:
        user = self.session.user
        transactions = user.get("transactions", [])
        trade_actions = {"BUY", "SELL", "LIMIT BUY", "LIMIT SELL", "STOP LOSS"}
        return {
            "trade_count": sum(1 for txn in transactions if txn.get("action") in trade_actions),
            "buy_count": sum(1 for txn in transactions if txn.get("action") in {"BUY", "LIMIT BUY"}),
            "sell_count": sum(1 for txn in transactions if txn.get("action") in {"SELL", "LIMIT SELL", "STOP LOSS"}),
            "news_read_count": int(user.get("news_read_count", 0) or 0),
            "order_activity": len(user.get("orders", [])) + sum(1 for txn in transactions if txn.get("action") in {"LIMIT BUY", "LIMIT SELL", "STOP LOSS"}),
            "portfolio_count": len(user.get("portfolio", {})),
            "net_worth": self.account_net_worth(user),
        }

    def ensure_daily_quests(self) -> None:
        user = self.session.user
        today = time.strftime("%Y-%m-%d")
        if user.get("daily_quest_day") == today and user.get("daily_quests"):
            return
        stats = self.daily_quest_stats()
        rng = random.Random(f"{self.session.username}:{today}")
        templates = [
            ("daily_quest_trade", "trade_count", 2, 4.0),
            ("daily_quest_buy", "buy_count", 1, 3.0),
            ("daily_quest_sell", "sell_count", 1, 3.0),
            ("daily_quest_news", "news_read_count", 2, 3.0),
            ("daily_quest_order", "order_activity", 1, 4.0),
            ("daily_quest_hold", "portfolio_count", 1, 4.0),
            ("daily_quest_net_worth", "net_worth", 5, 5.0),
        ]
        quests = []
        for label_key, metric, target, reward in rng.sample(templates, 3):
            quests.append(
                {
                    "label_key": label_key,
                    "metric": metric,
                    "target": target,
                    "reward": reward,
                    "start_value": stats.get(metric, 0),
                    "claimed": False,
                }
            )
        user["daily_quest_day"] = today
        user["daily_quests"] = quests

    def quest_progress(self, quest: dict, stats: dict | None = None) -> float:
        stats = stats or self.daily_quest_stats()
        current = float(stats.get(quest.get("metric", ""), 0) or 0)
        start = float(quest.get("start_value", 0) or 0)
        return max(0.0, current - start)

    def process_daily_quests(self) -> None:
        self.ensure_daily_quests()
        user = self.session.user
        stats = self.daily_quest_stats()
        rewards = 0.0
        completed = 0
        for quest in user.get("daily_quests", []):
            if quest.get("claimed"):
                continue
            if self.quest_progress(quest, stats) >= float(quest.get("target", 0) or 0):
                reward = float(quest.get("reward", 0.0) or 0.0)
                quest["claimed"] = True
                quest["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                user["cash"] = round(user.get("cash", 0) + reward, 2)
                self.record_transaction("QUEST", "DAILY", 1, reward)
                rewards += reward
                completed += 1
        if completed:
            self.status.set(self.tr("daily_quest_rewarded", count=completed, amount=money(rewards)))
            self.trigger_effect("achievement", "QUEST")

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
        macro = self.session.market_data.get("macro", {})
        if macro:
            summary_lines.append(
                f"{self.tr('macro')}: {self.tr('inflation')} {macro.get('inflation', 0):.2f}% | "
                f"{self.tr('rates')} {macro.get('interest_rate', 0):.2f}% | "
                f"{self.tr('oil')} {money(macro.get('oil_price', 0))}"
            )
        self.ensure_daily_quests()
        quest_stats = self.daily_quest_stats()
        summary_lines.append("")
        summary_lines.append(self.tr("daily_quests"))
        for quest in self.session.user.get("daily_quests", []):
            progress = min(self.quest_progress(quest, quest_stats), float(quest.get("target", 0) or 0))
            target = float(quest.get("target", 0) or 0)
            marker = "✓" if quest.get("claimed") else "○"
            reward = money(float(quest.get("reward", 0) or 0))
            summary_lines.append(f"{marker} {self.tr(quest.get('label_key', 'daily_quest_trade'))}: {progress:g}/{target:g} ({reward})")
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
            warning = "BREAK" if event.get("breaking") else "!" if event.get("misleading") else " "
            self.dashboard_news.insert(END, f"{warning:<5} {event.get('symbol', 'MARKET'):<6} {event.get('title', '')[:68]}")

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
        reputation = self.source_reputation_summary()
        if reputation:
            best = reputation[0]
            self.dashboard_news_quality.insert(END, self.tr("top_source", source=best["source"], hit_rate=best["hit_rate"], resolved=best["resolved"]))
            if len(reputation) > 1:
                watch = reputation[-1]
                self.dashboard_news_quality.insert(END, self.tr("watch_source", source=watch["source"], hit_rate=watch["hit_rate"], resolved=watch["resolved"]))
        self.dashboard_news_quality.insert(END, self.tr("news_quality_hint"))

    def source_reputation_summary(self) -> list[dict]:
        rows = []
        for source, row in self.session.market_data.get("source_reputation", {}).items():
            resolved = int(row.get("resolved", 0) or 0)
            if not resolved:
                continue
            helped = int(row.get("helped", 0) or 0)
            rows.append(
                {
                    "source": source,
                    "resolved": resolved,
                    "helped": helped,
                    "hit_rate": helped / resolved * 100,
                    "credibility": (float(row.get("credibility_total", 0.0) or 0.0) / resolved) * 100,
                }
            )
        return sorted(rows, key=lambda item: (item["hit_rate"], item["resolved"]), reverse=True)

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
        self.refreshing_market_list = True
        try:
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
                        self.market_list.activate(idx)
                        self.market_change_list.activate(idx)
                        self.market_list.see(idx)
                        self.market_change_list.see(idx)
                        break
        finally:
            self.refreshing_market_list = False

    def refresh_portfolio(self) -> None:
        previous_symbol = ""
        selection = self.portfolio_list.curselection()
        if selection and selection[0] < len(self.portfolio_symbols):
            previous_symbol = self.portfolio_symbols[selection[0]]
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
        if previous_symbol in self.portfolio_symbols:
            idx = self.portfolio_symbols.index(previous_symbol)
            self.portfolio_list.selection_set(idx)
            self.portfolio_list.activate(idx)
            self.portfolio_list.see(idx)

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
        loans = user.get("loans", [])
        selected_loan_id = ""
        selection = self.bank_list.curselection()
        if selection and selection[0] < len(loans):
            selected_loan_id = self.loan_identity(loans[selection[0]])
        for loan in loans:
            self.ensure_loan_terms(loan)
        bank_debt = self.total_bank_debt(user)
        credit_available = max(0.0, self.credit_limit(user) - self.used_credit(user))
        next_index = self.next_due_loan_index(loans)
        if hasattr(self, "bank_cash_value"):
            self.bank_cash_value.configure(text=money(user.get("cash", 0)))
            self.bank_debt_value.configure(text=money(bank_debt))
            self.bank_credit_value.configure(text=money(credit_available))
            if next_index is None:
                self.bank_next_payment_value.configure(text=self.tr("no_payment_due"))
                if hasattr(self, "bank_next_payment_detail"):
                    self.bank_next_payment_detail.configure(text=self.tr("no_payment_due"))
            else:
                next_loan = loans[next_index]
                target = self.suggested_bank_payment(next_loan, cap_to_cash=False)
                due = self.loan_due_date(next_loan)
                due_label = due[0] if due else self.tr("unknown_due")
                label = f"{money(target)} | {due_label}"
                self.bank_next_payment_value.configure(text=label)
                if hasattr(self, "bank_next_payment_detail"):
                    self.bank_next_payment_detail.configure(text=f"{self.tr('pay_next_due_help')} {label}")
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
        if not loans:
            self.bank_list.insert(END, self.tr("no_bank_debt"))
        for loan in loans:
            due = loan.get("due_at", self.tr("unknown_due"))
            self.bank_list.insert(
                END,
                (
                    f"{self.funding_type_label(loan.get('type', 'loan')):<10} "
                    f"{money(loan.get('balance', 0)):>10}  "
                    f"{self.tr('minimum')} {money(loan.get('minimum_payment', 0)):<10}  "
                    f"{self.tr('due')} {due:<12}  "
                    f"{self.tr('interest')} {loan.get('interest_rate', 0) * 100:.1f}%"
                ),
            )
        if selected_loan_id:
            for idx, loan in enumerate(loans):
                if self.loan_identity(loan) == selected_loan_id:
                    self.bank_list.selection_set(idx)
                    self.bank_list.activate(idx)
                    self.bank_list.see(idx)
                    break
        if hasattr(self, "bank_risk_list"):
            self.refresh_bank_risk_list(user)

    def refresh_bank_risk_list(self, user: dict) -> None:
        self.bank_risk_list.delete(0, END)
        has_risk_item = False
        if user.get("margin_debt", 0):
            has_risk_item = True
            self.bank_risk_list.insert(END, f"MARGIN      {self.tr('margin_debt')}: {money(user.get('margin_debt', 0))}  {self.tr('margin_available')}: {money(self.max_margin_available(user))}")
        for symbol, position in sorted(user.get("short_positions", {}).items()):
            item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
            current = item["price"] if item else position.get("entry_price", 0)
            liability = current * position.get("quantity", 0)
            has_risk_item = True
            self.bank_risk_list.insert(END, f"SHORT       {symbol:<6} {self.tr('qty')} {position.get('quantity', 0):.3f} {self.tr('entry')} {money(position.get('entry_price', 0))} {self.tr('liability')} {money(liability)}")
        for policy in user.get("insurance_policies", []):
            has_risk_item = True
            self.bank_risk_list.insert(END, f"{self.tr('hedge').upper():<11} {policy.get('symbol', ''):<6} {self.tr('floor')} {money(policy.get('floor_price', 0))} {self.tr('expires')} {policy.get('expires_at', '')}")
        if not has_risk_item:
            self.bank_risk_list.insert(END, self.tr("no_risk_positions"))

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

    def loan_identity(self, loan: dict) -> str:
        return f"{loan.get('created_at', '')}|{loan.get('type', '')}|{loan.get('principal', '')}|{loan.get('interest_rate', '')}"

    def next_due_loan_index(self, loans: list[dict]) -> int | None:
        candidates = []
        for index, loan in enumerate(loans):
            if loan.get("balance", 0) <= 0:
                continue
            self.ensure_loan_terms(loan)
            candidates.append((loan.get("due_at_ts", float("inf")), index))
        if not candidates:
            return None
        return min(candidates)[1]

    def suggested_bank_payment(self, loan: dict, cap_to_cash: bool = True) -> float:
        balance = max(0.0, float(loan.get("balance", 0.0) or 0.0))
        minimum = max(0.0, float(loan.get("minimum_payment", 0.0) or 0.0))
        target = min(balance, minimum if minimum > 0 else balance)
        if cap_to_cash:
            target = min(target, max(0.0, float(self.session.user.get("cash", 0.0) or 0.0)))
        return round(target, 2)

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
                    self.trigger_effect("success", "HEDGE")
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
            self.trigger_effect("risk", "RISK")
        return changed

    def request_simple_bank_funding(self) -> None:
        self.bank_funding_type.set(self.funding_type_label("loan"))
        self.request_bank_funding()

    def request_bank_funding(self) -> None:
        funding_type = self.funding_type_from_label(self.bank_funding_type.get())
        if funding_type not in LOAN_OPTIONS:
            funding_type = "loan"
        try:
            amount = float(self.bank_amount.get())
        except ValueError:
            self.trigger_effect("error", "ERROR")
            messagebox.showerror(self.tr("bank_request_rejected"), self.tr("amount_must_be_numeric"))
            return
        if amount <= 0:
            self.trigger_effect("error", "ERROR")
            messagebox.showerror(self.tr("bank_request_rejected"), self.tr("amount_must_be_positive"))
            return
        if amount > 1000:
            self.trigger_effect("error", "LIMIT")
            messagebox.showerror(self.tr("bank_request_rejected"), self.tr("bank_amount_limit"))
            return
        option = LOAN_OPTIONS[funding_type]
        interest_rate = option["rate"]
        balance = round(amount * (1 + interest_rate), 2)
        user = self.session.user
        if funding_type == "credit" and self.used_credit(user) + balance > self.credit_limit(user):
            self.trigger_effect("error", "LIMIT")
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
        self.trigger_effect("success", "BANK")
        self.refresh_all()

    def apply_bank_repayment(self, loan_index: int, amount: float) -> None:
        user = self.session.user
        loans = user.get("loans", [])
        if loan_index < 0 or loan_index >= len(loans):
            return
        loan = loans[loan_index]
        payment = min(amount, loan.get("balance", 0), user.get("cash", 0))
        if payment <= 0:
            return
        user["cash"] = round(user.get("cash", 0) - payment, 2)
        loan["balance"] = round(loan.get("balance", 0) - payment, 2)
        if loan["balance"] <= 0:
            loans.pop(loan_index)
            self.adjust_credit_score(20)
        elif payment >= loan.get("minimum_payment", 0):
            self.adjust_credit_score(5)
        self.record_transaction("REPAY", "BANK", payment, 1)
        self.status.set(self.tr("bank_repayment_recorded", amount=money(payment)))
        self.trigger_effect("success", "PAID")
        self.refresh_all()

    def repay_next_bank_debt(self) -> None:
        loans = self.session.user.get("loans", [])
        loan_index = self.next_due_loan_index(loans)
        if loan_index is None:
            return
        payment = self.suggested_bank_payment(loans[loan_index], cap_to_cash=True)
        if payment <= 0:
            self.trigger_effect("error", "CASH")
            messagebox.showerror(self.tr("repayment_rejected"), self.tr("not_enough_cash_repay"))
            return
        self.apply_bank_repayment(loan_index, payment)

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
            self.trigger_effect("error", "ERROR")
            messagebox.showerror(self.tr("repayment_rejected"), self.tr("amount_must_be_numeric"))
            return
        if amount <= 0:
            self.trigger_effect("error", "ERROR")
            messagebox.showerror(self.tr("repayment_rejected"), self.tr("amount_must_be_positive"))
            return
        user = self.session.user
        if amount > user.get("cash", 0):
            self.trigger_effect("error", "CASH")
            messagebox.showerror(self.tr("repayment_rejected"), self.tr("not_enough_cash_repay"))
            return
        self.apply_bank_repayment(selection[0], amount)

    def request_margin(self) -> None:
        try:
            amount = float(self.margin_amount.get())
        except ValueError:
            self.trigger_effect("error", "ERROR")
            messagebox.showerror(self.tr("margin_rejected"), self.tr("amount_must_be_numeric"))
            return
        if amount <= 0:
            self.trigger_effect("error", "ERROR")
            messagebox.showerror(self.tr("margin_rejected"), self.tr("amount_must_be_positive"))
            return
        user = self.session.user
        available = self.max_margin_available(user)
        if amount > available:
            self.trigger_effect("error", "LIMIT")
            messagebox.showerror(self.tr("margin_rejected"), self.tr("margin_limit_reached", limit=money(available)))
            return
        user["cash"] = round(user.get("cash", 0) + amount, 2)
        user["margin_debt"] = round(float(user.get("margin_debt", 0.0) or 0.0) + amount, 2)
        self.record_transaction("MARGIN", "BANK", amount, 1)
        self.status.set(self.tr("margin_approved", amount=money(amount)))
        self.trigger_effect("risk", "MARGIN")
        self.refresh_all()

    def repay_margin(self) -> None:
        try:
            amount = float(self.margin_repayment.get())
        except ValueError:
            self.trigger_effect("error", "ERROR")
            messagebox.showerror(self.tr("repayment_rejected"), self.tr("amount_must_be_numeric"))
            return
        user = self.session.user
        if amount <= 0:
            self.trigger_effect("error", "ERROR")
            messagebox.showerror(self.tr("repayment_rejected"), self.tr("amount_must_be_positive"))
            return
        payment = min(amount, user.get("cash", 0), float(user.get("margin_debt", 0.0) or 0.0))
        if payment <= 0:
            return
        user["cash"] = round(user.get("cash", 0) - payment, 2)
        user["margin_debt"] = round(float(user.get("margin_debt", 0.0) or 0.0) - payment, 2)
        self.record_transaction("MARGIN REPAY", "BANK", payment, 1)
        self.status.set(self.tr("margin_repaid", amount=money(payment)))
        self.trigger_effect("success", "PAID")
        self.refresh_all()

    def short_sell(self) -> None:
        symbol = (self.short_symbol.get().strip().upper() or self.selected_symbol.get())
        item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
        if not item:
            self.trigger_effect("error", "SYMBOL")
            messagebox.showerror(self.tr("short_rejected"), self.tr("unknown_symbol"))
            return
        try:
            quantity = float(self.short_quantity.get())
        except ValueError:
            self.trigger_effect("error", "ERROR")
            messagebox.showerror(self.tr("short_rejected"), self.tr("amount_must_be_numeric"))
            return
        if quantity <= 0:
            self.trigger_effect("error", "ERROR")
            messagebox.showerror(self.tr("short_rejected"), self.tr("amount_must_be_positive"))
            return
        notional = item["price"] * quantity
        equity = self.account_net_worth(self.session.user)
        if equity < notional * SHORT_COLLATERAL_RATE:
            self.trigger_effect("error", "RISK")
            messagebox.showerror(self.tr("short_rejected"), self.tr("short_collateral_needed", amount=money(notional * SHORT_COLLATERAL_RATE)))
            return
        position = self.session.user.setdefault("short_positions", {}).get(symbol, {"quantity": 0.0, "entry_price": item["price"]})
        total_qty = position.get("quantity", 0.0) + quantity
        avg_entry = ((position.get("entry_price", item["price"]) * position.get("quantity", 0.0)) + notional) / total_qty
        self.session.user["short_positions"][symbol] = {"quantity": round(total_qty, 3), "entry_price": round(avg_entry, 2)}
        self.session.user["cash"] = round(self.session.user.get("cash", 0) + notional, 2)
        self.record_transaction("SHORT", symbol, quantity, item["price"])
        self.status.set(self.tr("short_opened", symbol=symbol, amount=money(notional)))
        self.trigger_effect("risk", "SHORT")
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
            self.trigger_effect("error", "ERROR")
            messagebox.showerror(self.tr("short_rejected"), self.tr("amount_must_be_numeric"))
            return
        cost = quantity * item["price"]
        if cost > self.session.user.get("cash", 0):
            self.trigger_effect("error", "CASH")
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
        self.trigger_effect("success", "COVER")
        self.refresh_all()
        self.pulse_chart_latest("trade")

    def buy_insurance(self) -> None:
        symbol = (self.insurance_symbol.get().strip().upper() or self.selected_symbol.get())
        item = next((asset_item for asset_item in self.get_assets() if asset_item["symbol"] == symbol), None)
        qty = self.session.user.get("portfolio", {}).get(symbol, 0)
        if not item or qty <= 0:
            self.trigger_effect("error", "HOLD")
            messagebox.showerror(self.tr("insurance_rejected"), self.tr("insurance_requires_holding"))
            return
        covered_value = item["price"] * qty
        premium = round(covered_value * INSURANCE_PREMIUM_RATE, 2)
        if premium > self.session.user.get("cash", 0):
            self.trigger_effect("error", "CASH")
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
        self.trigger_effect("success", "HEDGE")
        self.refresh_all()

    def refresh_orders(self) -> None:
        if not hasattr(self, "orders_list"):
            return
        orders = self.session.user.get("orders", [])
        selected_order_id = ""
        selection = self.orders_list.curselection()
        if selection and selection[0] < len(orders):
            selected_order_id = self.order_identity(orders[selection[0]])
        self.orders_list.delete(0, END)
        if not orders:
            self.orders_list.insert(END, self.tr("no_active_orders"))
            return
        for idx, order in enumerate(orders):
            self.orders_list.insert(
                END,
                f"{order.get('created_at', '')}  {order.get('type', ''):<10} {order.get('symbol', ''):<6} "
                f"{order.get('quantity', 0):>8.3f} target {money(order.get('target_price', 0))}",
            )
            if selected_order_id and self.order_identity(order) == selected_order_id:
                self.orders_list.selection_set(idx)
                self.orders_list.activate(idx)
                self.orders_list.see(idx)

    def order_identity(self, order: dict) -> str:
        return (
            f"{order.get('created_at', '')}|{order.get('type', '')}|{order.get('symbol', '')}|"
            f"{order.get('quantity', '')}|{order.get('target_price', '')}"
        )

    def localized_news_title(self, event: dict) -> str:
        key = event.get("title_key", "")
        values = event.get("title_values", {})
        if key:
            try:
                if isinstance(values, dict):
                    return self.tr(key, **values)
                return self.tr(key)
            except (KeyError, ValueError):
                return self.tr(key)
        return event.get("title") or event.get("message") or self.tr("news")

    def source_reputation_row(self, source: str) -> dict:
        reputation = self.session.market_data.setdefault("source_reputation", {})
        return reputation.get(source, {})

    def source_reputation_text(self, event: dict) -> str:
        source = event.get("source", "Market Desk")
        row = self.source_reputation_row(source)
        resolved = int(row.get("resolved", 0) or 0)
        if not resolved:
            return self.tr("source_reputation_pending", source=source)
        helped = int(row.get("helped", 0) or 0)
        hit_rate = helped / resolved * 100
        avg_credibility = float(row.get("credibility_total", 0.0) or 0.0) / resolved * 100
        return self.tr("source_reputation", source=source, hit_rate=hit_rate, helped=helped, resolved=resolved, credibility=avg_credibility)

    def normalize_news_event(self, event: dict) -> dict:
        message = event.get("message", "")
        title = self.localized_news_title(event)
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
        previous_id = self.selected_news_id
        selection = self.news_list.curselection()
        if selection and selection[0] < len(self.visible_news):
            previous_id = self.news_event_id(self.visible_news[selection[0]])
        self.news_list.delete(0, END)
        news_filter = self.news_filter.get()
        news_view = self.news_view_from_label(self.news_view.get())
        search = self.news_search.get().strip().lower()
        feed = self.session.market_data.get("news_feed", [])
        self.visible_news = []
        for event in reversed(feed):
            normalized = self.normalize_news_event(event)
            if self.news_matches_filters(normalized, news_filter, news_view, search):
                self.visible_news.append(normalized)
        if not self.visible_news:
            self.news_list.insert(END, self.tr("no_matching_news"))
            self.selected_news_id = ""
            self.render_news_article(None)
            return
        self.visible_news = self.visible_news[:140]
        read_news = set(self.session.user.setdefault("read_news", []))
        bookmarks = set(self.session.user.setdefault("bookmarked_news", []))
        for event in self.visible_news:
            event_id = self.news_event_id(event)
            state = "★" if event_id in bookmarks else "✓" if event_id in read_news else "•"
            if event.get("breaking"):
                state = "⚡"
            warning = " !" if event.get("misleading") else ""
            self.news_list.insert(END, f"{state} {event.get('time', '')}  {event.get('symbol', ''):<6}  {event.get('title', '')}{warning}")
        selected_index = 0
        if previous_id:
            for idx, event in enumerate(self.visible_news):
                if self.news_event_id(event) == previous_id:
                    selected_index = idx
                    break
        self.news_list.selection_set(selected_index)
        self.news_list.activate(selected_index)
        self.news_list.see(selected_index)
        selected_event = self.visible_news[selected_index]
        self.selected_news_id = self.news_event_id(selected_event)
        self.render_news_article(selected_event)

    def news_matches_filters(self, event: dict, category_filter: str, view_filter: str, search: str) -> bool:
        if category_filter != "All" and event.get("category") != category_filter:
            return False
        event_id = self.news_event_id(event)
        read_news = set(self.session.user.setdefault("read_news", []))
        bookmarks = set(self.session.user.setdefault("bookmarked_news", []))
        if view_filter == "unread" and event_id in read_news:
            return False
        if view_filter == "bookmarked" and event_id not in bookmarks:
            return False
        if not search:
            return True
        haystack = " ".join(
            str(event.get(key, ""))
            for key in ("time", "symbol", "category", "title", "message", "source", "source_type", "body", "insight")
        ).lower()
        return search in haystack

    def clear_news_search(self) -> None:
        self.news_search.set("")
        self.refresh_news()

    def on_select_news(self, _event=None) -> None:
        selection = self.news_list.curselection()
        if not selection or selection[0] >= len(self.visible_news):
            return
        event = self.visible_news[selection[0]]
        self.selected_news_id = self.news_event_id(event)
        self.mark_news_read(event)
        self.render_news_article(event)

    def news_event_id(self, event: dict) -> str:
        return f"{event.get('time', '')}|{event.get('symbol', '')}|{event.get('title', event.get('message', ''))}"

    def latest_breaking_news_id(self) -> str:
        for event in reversed(self.session.market_data.get("news_feed", [])):
            if event.get("breaking"):
                return self.news_event_id(event)
        return ""

    def handle_breaking_news_alerts(self) -> None:
        latest = None
        for event in reversed(self.session.market_data.get("news_feed", [])):
            if event.get("breaking"):
                latest = self.normalize_news_event(event)
                break
        if not latest:
            return
        event_id = self.news_event_id(latest)
        if event_id == self.last_breaking_news_id:
            return
        self.last_breaking_news_id = event_id
        self.status.set(self.tr("breaking_news_alert", title=latest.get("title", "")))
        self.trigger_effect("risk", "NEWS")

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
            self.news_source_reputation.configure(text="")
            self.news_impact_timeline.configure(text="")
            self.news_select_button.state(["disabled"])
            if hasattr(self, "news_bookmark_button"):
                self.news_bookmark_button.state(["disabled"])
                self.news_unread_button.state(["disabled"])
            self.draw_news_image("empty", None)
            return
        credibility = event.get("credibility", 0.6) * 100
        risk = self.tr("misleading_warning") if event.get("misleading") else self.tr("credibility_note")
        meta = (
            f"{event.get('time', '')} | {event.get('source', '')} ({event.get('source_type', '')}) | "
            f"{self.tr('symbol')}: {event.get('symbol', 'MARKET')} | "
            f"{self.tr('credibility')}: {credibility:.0f}% | {risk}"
        )
        if event.get("outcome"):
            if event.get("outcome") == "pending":
                meta += f" | {self.tr('impact_outcome')}: {self.tr('pending_impact')}"
            else:
                actual = float(event.get("actual_return", 0.0) or 0.0) * 100
                meta += f" | {self.tr('impact_outcome')}: {self.tr(event.get('outcome', 'mixed'))} ({actual:+.1f}%)"
        self.news_title.configure(text=event.get("title", ""))
        self.news_meta.configure(text=meta)
        self.news_body.configure(text=event.get("body", ""))
        self.news_insight.configure(text=f"{self.tr('investment_insight')}: {event.get('insight', '')}")
        self.news_source_reputation.configure(text=self.source_reputation_text(event))
        self.news_impact_timeline.configure(text=self.news_impact_timeline_text(event))
        symbol = event.get("symbol", "")
        if symbol and symbol != "MARKET" and any(item["symbol"] == symbol for item in self.get_assets()):
            self.news_select_button.state(["!disabled"])
        else:
            self.news_select_button.state(["disabled"])
        self.update_news_action_buttons(event)
        self.draw_news_image(event.get("image_key", "newspaper"), event)

    def news_impact_timeline_text(self, event: dict) -> str:
        if not event.get("impact_end_tick"):
            return self.tr("impact_timeline_none")
        start_tick = event.get("created_tick", "?")
        end_tick = event.get("impact_end_tick", "?")
        start_price = money(float(event.get("start_price", 0.0) or 0.0))
        if event.get("outcome") == "pending":
            return self.tr("impact_timeline_pending", start_tick=start_tick, end_tick=end_tick, start_price=start_price)
        end_price = money(float(event.get("end_price", 0.0) or 0.0))
        actual = float(event.get("actual_return", 0.0) or 0.0) * 100
        outcome = self.tr(event.get("outcome", "mixed"))
        return self.tr("impact_timeline_resolved", start_tick=start_tick, end_tick=end_tick, start_price=start_price, end_price=end_price, actual=actual, outcome=outcome)

    def selected_news_event(self) -> dict | None:
        if not hasattr(self, "news_list"):
            return None
        selection = self.news_list.curselection()
        if not selection or selection[0] >= len(self.visible_news):
            return None
        return self.visible_news[selection[0]]

    def update_news_action_buttons(self, event: dict | None) -> None:
        if not hasattr(self, "news_bookmark_button"):
            return
        if not event:
            self.news_bookmark_button.state(["disabled"])
            self.news_unread_button.state(["disabled"])
            return
        event_id = self.news_event_id(event)
        bookmarks = set(self.session.user.setdefault("bookmarked_news", []))
        label_key = "remove_bookmark" if event_id in bookmarks else "bookmark"
        self.news_bookmark_button.configure(text=self.with_icon("★", label_key))
        self.news_bookmark_button.state(["!disabled"])
        self.news_unread_button.state(["!disabled"])

    def toggle_news_bookmark(self) -> None:
        event = self.selected_news_event()
        if not event:
            return
        event_id = self.news_event_id(event)
        bookmarks = self.session.user.setdefault("bookmarked_news", [])
        if event_id in bookmarks:
            bookmarks.remove(event_id)
            self.status.set(self.tr("bookmark_removed"))
        else:
            bookmarks.append(event_id)
            del bookmarks[:-200]
            self.status.set(self.tr("bookmark_saved"))
        self.session.save()
        self.refresh_news()

    def mark_selected_news_unread(self) -> None:
        event = self.selected_news_event()
        if not event:
            return
        event_id = self.news_event_id(event)
        read_news = self.session.user.setdefault("read_news", [])
        if event_id in read_news:
            read_news.remove(event_id)
            self.session.save()
        self.status.set(self.tr("marked_unread"))
        self.refresh_news()

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
        elif image_key == "breaking":
            canvas.create_rectangle(0, 0, width, height, fill="#7f1d1d", outline="")
            canvas.create_rectangle(20, 24, width - 20, 68, fill="#fef2f2", outline="")
            canvas.create_text(36, 46, anchor="w", text="BREAKING NEWS", fill="#991b1b", font=("Arial", 24, "bold"))
            canvas.create_line(32, 104, width - 40, 104, fill="#fca5a5", width=5)
            canvas.create_polygon(width - 118, 86, width - 64, 86, width - 92, 132, fill="#fbbf24", outline="")
            canvas.create_text(36, 132, anchor="w", text=title, fill="#fee2e2", font=("Arial", 22, "bold"))
        elif image_key == "earnings":
            canvas.create_rectangle(0, 0, width, height, fill="#ecfeff", outline="")
            canvas.create_rectangle(34, 28, width - 34, 132, fill="#ffffff", outline="#0891b2", width=2)
            bars = [42, 76, 58, 104, 88]
            for index, bar_height in enumerate(bars):
                x = 74 + index * 42
                canvas.create_rectangle(x, 122 - bar_height, x + 22, 122, fill="#0ea5e9", outline="")
            canvas.create_line(330, 112, 380, 78, 430, 90, 500, 42, fill="#16a34a", width=4)
            canvas.create_text(48, 48, anchor="w", text="EARNINGS", fill="#155e75", font=("Arial", 20, "bold"))
        elif image_key == "lawsuit":
            canvas.create_rectangle(0, 0, width, height, fill="#f8fafc", outline="")
            canvas.create_rectangle(42, 106, 180, 124, fill="#78350f", outline="")
            canvas.create_polygon(74, 40, 146, 40, 160, 106, 60, 106, fill="#fbbf24", outline="#92400e", width=2)
            canvas.create_line(110, 40, 110, 106, fill="#92400e", width=3)
            canvas.create_line(78, 62, 142, 62, fill="#92400e", width=3)
            canvas.create_text(230, 50, anchor="w", text="LEGAL RISK", fill="#92400e", font=("Arial", 22, "bold"))
            canvas.create_text(230, 92, anchor="w", text=title, fill="#0f172a", font=("Arial", 18, "bold"))
        elif image_key == "crypto":
            canvas.create_rectangle(0, 0, width, height, fill="#111827", outline="")
            canvas.create_oval(46, 28, 152, 134, fill="#f59e0b", outline="#fde68a", width=4)
            canvas.create_text(99, 82, text="₿", fill="#111827", font=("Arial", 46, "bold"))
            for x in [220, 278, 336, 394, 452]:
                canvas.create_oval(x, 64, x + 12, 76, fill="#38bdf8", outline="")
                canvas.create_line(x + 12, 70, x + 46, 70, fill="#38bdf8", width=2)
            canvas.create_text(218, 38, anchor="w", text="DIGITAL ASSETS", fill="#bfdbfe", font=("Arial", 20, "bold"))
        elif image_key == "fund":
            canvas.create_rectangle(0, 0, width, height, fill="#f0fdf4", outline="")
            canvas.create_rectangle(42, 110, 100, 130, fill="#16a34a", outline="")
            canvas.create_rectangle(124, 82, 182, 130, fill="#22c55e", outline="")
            canvas.create_rectangle(206, 58, 264, 130, fill="#4ade80", outline="")
            canvas.create_rectangle(288, 34, 346, 130, fill="#86efac", outline="")
            canvas.create_line(390, 124, width - 52, 46, fill="#15803d", width=4)
            canvas.create_text(42, 36, anchor="w", text="FUND FLOW", fill="#166534", font=("Arial", 22, "bold"))
        elif image_key == "rates":
            canvas.create_rectangle(0, 0, width, height, fill="#eff6ff", outline="")
            canvas.create_line(52, 124, width - 54, 124, fill="#1e3a8a", width=3)
            canvas.create_line(52, 124, 52, 34, fill="#1e3a8a", width=3)
            canvas.create_line(72, 104, 160, 88, 248, 98, 336, 62, 448, 54, fill="#2563eb", width=4)
            canvas.create_text(64, 44, anchor="w", text="RATES / MACRO", fill="#1e3a8a", font=("Arial", 20, "bold"))
            canvas.create_text(width - 54, 92, anchor="e", text="%", fill="#60a5fa", font=("Arial", 48, "bold"))
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
        if self.refreshing_market_list:
            return
        source = _event.widget if _event else self.market_list
        selection = source.curselection()
        if not selection or selection[0] >= len(self.visible_assets):
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
            self.trigger_effect("error", "ERROR")
            messagebox.showerror("Order rejected", "Unknown symbol.")
            return
        try:
            quantity = float(self.order_quantity.get())
            target_price = float(self.order_price.get())
        except ValueError:
            self.trigger_effect("error", "ERROR")
            messagebox.showerror("Order rejected", "Quantity and target price must be numeric.")
            return
        if quantity <= 0 or target_price <= 0:
            self.trigger_effect("error", "ERROR")
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
        self.trigger_effect("order", "ORDER")
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
        self.trigger_effect("order", "CANCEL")
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
            self.trigger_effect("order", f"{triggered} ORDER")
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
        financials = item.get("financials", {})
        dividend_text = ""
        if item.get("category") in {"Stock", "Fund"}:
            dividend_text = (
                f" | {self.tr('dividend_yield')} {float(item.get('dividend_yield', 0) or 0) * 100:.2f}% "
                f"| {self.tr('ex_dividend_tick')} {item.get('next_dividend_tick', 0)}"
            )
        self.asset_meta.configure(
            text=(
                f"{item['category']} | {item.get('sector', 'General')} | "
                f"Price {money(item['price'])} | Owned {owned:.3f} | "
                f"{self.tr('risk_rating')}: {financials.get('risk_rating', 'Medium')} | "
                f"{self.tr('sector_outlook')}: {financials.get('sector_outlook', 'Stable')}{dividend_text}\n"
                f"{self.tr('revenue')}: {money(financials.get('revenue', 0))} | "
                f"{self.tr('profit_margin')}: {float(financials.get('profit_margin', 0) or 0) * 100:.1f}% | "
                f"{self.tr('growth')}: {float(financials.get('growth', 0) or 0) * 100:.1f}% | "
                f"{self.tr('debt_ratio')}: {float(financials.get('debt_ratio', 0) or 0) * 100:.1f}% | "
                f"{self.tr('earnings')}: {financials.get('last_earnings', 'in line')} ({financials.get('earnings_in_ticks', '?')} {self.tr('ticks')})\n"
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
            self.trigger_effect("error", "ERROR")
            messagebox.showerror("Invalid quantity", "Enter a numeric quantity.")
            return None
        if qty <= 0:
            self.trigger_effect("error", "ERROR")
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
            self.trigger_effect("error", "CASH")
            messagebox.showerror("Not enough cash", f"Need {money(cost)}, but you have {money(user['cash'])}.")
            return
        user["cash"] = round(user["cash"] - cost, 2)
        user.setdefault("portfolio", {})[item["symbol"]] = round(user.get("portfolio", {}).get(item["symbol"], 0) + qty, 3)
        self.record_transaction("BUY", item["symbol"], qty, item["price"])
        self.status.set(f"Bought {qty:.3f} {item['symbol']} for {money(cost)}.")
        self.refresh_all()
        self.trigger_effect("trade", "BUY")
        self.pulse_chart_latest("trade")

    def sell_selected(self) -> None:
        item = self.selected_asset()
        qty = self.parse_quantity()
        if not item or qty is None:
            return
        user = self.session.user
        owned = user.get("portfolio", {}).get(item["symbol"], 0)
        if qty > owned:
            self.trigger_effect("error", "HOLD")
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
        self.trigger_effect("sell", "SELL")
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
        current_tick = int(self.session.market_data.get("tick_count", 0) or 0)
        for item in self.get_assets():
            if item.get("category") not in {"Stock", "Fund"}:
                continue
            next_tick = int(item.get("next_dividend_tick", 0) or 0)
            if not next_tick or current_tick < next_tick:
                continue
            symbol = item.get("symbol", "")
            qty = float(user.get("portfolio", {}).get(symbol, 0) or 0)
            rate = max(0.001, float(item.get("dividend_yield", 0.0) or 0.0) / 4)
            if qty > 0:
                dividend = round(item["price"] * qty * rate, 2)
                if dividend > 0:
                    user["cash"] = round(user.get("cash", 0) + dividend, 2)
                    self.record_transaction("DIVIDEND", symbol, qty, dividend / qty if qty else dividend)
                    self.session.market_data.setdefault("news_feed", []).append(
                        {
                            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "symbol": symbol,
                            "category": item.get("category", "Stock"),
                            "message": f"{symbol} paid a scheduled dividend to holders.",
                            "title": f"{symbol} reaches ex-dividend date",
                            "body": f"{item.get('name', symbol)} paid holders a scheduled dividend based on its current dividend yield.",
                            "source": "Market Desk",
                            "source_type": "Newswire",
                            "credibility": 0.9,
                            "impact": "mixed",
                            "insight": "Dividend income improves cash, but the asset price can still move independently.",
                            "image_key": "newspaper",
                            "misleading": False,
                        }
                    )
            item["next_dividend_tick"] = current_tick + int(item.get("dividend_interval_ticks", 60) or 60)

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
        self.handle_breaking_news_alerts()

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
            self.trigger_effect("order", "PAUSE")
        else:
            self.start_live_updates()
            self.status.set(f"Market updates resumed at {self.current_interval_seconds():.1f}s per tick.")
            self.trigger_effect("success", "LIVE")

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
        self.trigger_effect("success", "SPEED")

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
        self.handle_breaking_news_alerts()
        self.schedule_live_update()
