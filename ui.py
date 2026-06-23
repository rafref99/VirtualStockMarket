from __future__ import annotations

import platform
import time
from tkinter import BOTH, END, LEFT, RIGHT, X, Y, BooleanVar, Canvas, Listbox, StringVar, Tk, messagebox
from tkinter import ttk

from config import APP_SETTINGS_FILE, CHART_RANGES, DATA_DIR, MARKET_FILE, STARTING_CURRENCY, USERS_FILE, money
from i18n import LANGUAGES, THEMES, TRANSLATIONS
from market import advance_market, generate_market
from storage import Session, create_user_record, ensure_data_dir, load_json, save_json, verify_password

class VirtualStockMarketApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("Virtual Stock Market")
        self.root.geometry("1180x760")
        self.root.minsize(980, 620)
        self.session: Session | None = None
        self.selected_symbol = StringVar()
        self.status = StringVar(value="Welcome to the fake currency market.")
        self.live_updates_enabled = False
        self.live_update_job: str | None = None
        self.live_interval_seconds = StringVar(value="3")
        self.language = StringVar(value="English")
        self.dark_mode = BooleanVar(value=False)
        self.live_button_text = StringVar(value="")
        self.chart_range = StringVar(value="Days")
        self.chart_points: list[dict] = []
        self.portfolio_symbols: list[str] = []
        self.logo_canvas: Canvas | None = None
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
        style.configure("TButton", padding=6)
        style.configure("TCheckbutton", background=colors["bg"], foreground=colors["text"])
        style.configure("TRadiobutton", background=colors["bg"], foreground=colors["text"])
        style.configure("TNotebook", background=colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", padding=(12, 6), background=colors["panel"], foreground=colors["text"])
        style.map("TNotebook.Tab", background=[("selected", colors["select_bg"])], foreground=[("selected", colors["select_fg"])])
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

    def update_live_button_text(self) -> None:
        key = "freeze" if self.live_updates_enabled else "resume"
        icon = "⏸" if self.live_updates_enabled else "▶"
        self.live_button_text.set(self.with_icon(icon, key))

    def ensure_user_settings(self) -> dict:
        user = self.session.user
        settings = user.setdefault("settings", {})
        settings.setdefault("language", "English")
        settings.setdefault("dark_mode", False)
        return settings

    def load_user_preferences(self) -> None:
        settings = self.ensure_user_settings()
        language = settings.get("language", "English")
        self.language.set(language if language in LANGUAGES else "English")
        self.dark_mode.set(bool(settings.get("dark_mode", False)))
        self.apply_theme()
        self.update_live_button_text()

    def save_user_preferences(self) -> None:
        if not self.session:
            return
        settings = self.ensure_user_settings()
        settings["language"] = self.language.get()
        settings["dark_mode"] = bool(self.dark_mode.get())
        self.session.save()

    def load_app_settings(self) -> dict:
        return load_json(APP_SETTINGS_FILE, {"remembered_username": ""})

    def save_remembered_username(self, username: str) -> None:
        save_json(APP_SETTINGS_FILE, {"remembered_username": username if self.remember_me.get() else ""})

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
        ttk.Checkbutton(fields, text=self.tr("remember_me"), variable=self.remember_me).pack(anchor="w", pady=(0, 18))

        buttons = ttk.Frame(card)
        buttons.pack(fill=X)
        ttk.Button(buttons, text=self.with_icon("🔐", "login"), command=lambda: self.login(username.get(), password.get())).pack(side=LEFT, expand=True, fill=X, padx=(0, 6))
        ttk.Button(buttons, text=self.with_icon("＋", "register"), command=lambda: self.register(username.get(), password.get())).pack(side=RIGHT, expand=True, fill=X, padx=(6, 0))

        ttk.Label(card, text=self.tr("local_files"), foreground=self.colors()["muted"]).pack(pady=(18, 0))

    def load_session(self, username: str) -> Session:
        market = load_json(MARKET_FILE, {"last_tick": time.time(), "assets": generate_market()})
        elapsed = int((time.time() - market.get("last_tick", time.time())) // 15)
        advance_market(market, ticks=min(max(elapsed, 1), 10))
        users = load_json(USERS_FILE, {"users": {}})
        return Session(username=username, users_data=users, market_data=market)

    def register(self, username: str, password: str) -> None:
        username = username.strip().lower()
        if len(username) < 3 or not username.replace("_", "").isalnum():
            messagebox.showerror("Registration failed", "Use at least 3 letters, numbers, or underscores.")
            return
        if len(password) < 4:
            messagebox.showerror("Registration failed", "Use a password with at least 4 characters.")
            return
        users = load_json(USERS_FILE, {"users": {}})
        if username in users["users"]:
            messagebox.showerror("Registration failed", "That username already exists.")
            return
        users["users"][username] = create_user_record(username, password)
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
        ttk.Button(sidebar, text=self.with_icon("▶", "manual_tick"), command=self.tick).pack(fill=X, pady=3)
        ttk.Button(sidebar, textvariable=self.live_button_text, command=self.toggle_live_updates).pack(fill=X, pady=3)

        speed_frame = ttk.Frame(sidebar)
        speed_frame.pack(fill=X, pady=(8, 3))
        ttk.Label(speed_frame, text=self.tr("step_speed")).pack(anchor="w")
        ttk.Entry(speed_frame, textvariable=self.live_interval_seconds, width=8).pack(side=LEFT, fill=X, expand=True, pady=(2, 0))
        ttk.Button(speed_frame, text=self.with_icon("✓", "apply"), command=self.apply_live_speed).pack(side=RIGHT, padx=(6, 0), pady=(2, 0))

        ttk.Button(sidebar, text=self.with_icon("↻", "refresh"), command=self.refresh_all).pack(fill=X, pady=3)
        ttk.Button(sidebar, text=self.with_icon("⇥", "logout"), command=self.logout).pack(fill=X, pady=(20, 3))
        ttk.Label(sidebar, textvariable=self.status, wraplength=220, foreground=self.colors()["muted"]).pack(anchor="w", pady=(24, 0))

        notebook = ttk.Notebook(main)
        notebook.grid(row=0, column=0, sticky="nsew")
        market_tab = ttk.Frame(notebook, padding=14)
        settings_tab = ttk.Frame(notebook, padding=14)
        market_tab.rowconfigure(2, weight=1)
        market_tab.columnconfigure(0, weight=1)
        notebook.add(market_tab, text=self.with_icon("📈", "market"))
        notebook.add(settings_tab, text=self.with_icon("⚙", "settings"))
        self.build_settings_tab(settings_tab)

        filters = ttk.Frame(market_tab)
        filters.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(filters, text=self.tr("market"), font=("Arial", 22, "bold")).pack(side=LEFT)
        self.filter_var = StringVar(value="All")
        for category in ["All", "Stock", "Crypto", "FNT", "Commodity", "Fund"]:
            ttk.Radiobutton(filters, text=category, variable=self.filter_var, value=category, command=self.refresh_market_list).pack(side=LEFT, padx=8)

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
        ttk.Button(trade, text=self.with_icon("▲", "buy"), command=self.buy_selected).pack(side=LEFT, padx=4)
        ttk.Button(trade, text=self.with_icon("▼", "sell"), command=self.sell_selected).pack(side=LEFT, padx=4)

        ttk.Label(detail, text=self.tr("portfolio"), font=("Arial", 16, "bold")).pack(anchor="w", pady=(20, 4))
        self.portfolio_list = Listbox(detail, height=8, exportselection=False)
        self.configure_listbox(self.portfolio_list)
        self.portfolio_list.pack(fill=BOTH, expand=True)
        self.portfolio_list.bind("<Double-Button-1>", self.on_portfolio_double_click)

        self.refresh_all()
        if start_live:
            self.start_live_updates()
        else:
            self.stop_live_updates()

    def build_settings_tab(self, parent) -> None:
        parent.columnconfigure(0, weight=1)
        account_box = ttk.LabelFrame(parent, text=self.tr("account"), padding=14)
        account_box.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(account_box, text=f"{self.tr('username')}: {self.session.username}", font=("Arial", 12, "bold")).pack(anchor="w")
        ttk.Label(account_box, text=f"{self.tr('created')}: {self.session.user.get('created_at', 'Unknown')}").pack(anchor="w", pady=(4, 0))

        appearance_box = ttk.LabelFrame(parent, text=self.tr("appearance"), padding=14)
        appearance_box.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        ttk.Checkbutton(appearance_box, text=self.with_icon("◐", "dark_mode"), variable=self.dark_mode, command=self.apply_settings_change).pack(anchor="w")

        language_box = ttk.LabelFrame(parent, text=self.tr("language"), padding=14)
        language_box.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        language_selector = ttk.Combobox(language_box, textvariable=self.language, values=LANGUAGES, state="readonly", width=22)
        language_selector.pack(anchor="w")
        language_selector.bind("<<ComboboxSelected>>", lambda _event: self.apply_settings_change())

        system_box = ttk.LabelFrame(parent, text=self.tr("system"), padding=14)
        system_box.grid(row=3, column=0, sticky="ew")
        ttk.Label(
            system_box,
            text=self.tr("system_info", python=platform.python_version(), assets=len(self.get_assets())),
            foreground=self.colors()["muted"],
        ).pack(anchor="w")
        ttk.Label(system_box, text=f"Data: {DATA_DIR}", foreground=self.colors()["muted"]).pack(anchor="w", pady=(4, 0))

    def apply_settings_change(self) -> None:
        was_live = self.live_updates_enabled
        self.save_user_preferences()
        self.apply_theme()
        self.status.set(self.tr("saved"))
        self.show_dashboard(start_live=was_live)

    def logout(self) -> None:
        self.stop_live_updates()
        if self.session:
            self.session.save()
        self.session = None
        self.status.set("Logged out.")
        self.show_login()

    def get_assets(self) -> list[dict]:
        assert self.session is not None
        return self.session.market_data["assets"]

    def selected_asset(self) -> dict | None:
        symbol = self.selected_symbol.get()
        return next((item for item in self.get_assets() if item["symbol"] == symbol), None)

    def refresh_all(self) -> None:
        if not self.session:
            return
        self.session.save()
        self.refresh_account()
        self.refresh_market_list()
        self.refresh_portfolio()
        self.render_selected()

    def refresh_account(self) -> None:
        user = self.session.user
        holdings_value = 0.0
        for symbol, qty in user.get("portfolio", {}).items():
            found = next((a for a in self.get_assets() if a["symbol"] == symbol), None)
            if found:
                holdings_value += found["price"] * qty
        self.account_label.configure(
            text=(
                f"{self.tr('username')}: {self.session.username}\n"
                f"{self.tr('cash')}: {money(user.get('cash', 0))}\n"
                f"{self.tr('holdings')}: {money(holdings_value)}\n"
                f"{self.tr('net_worth')}: {money(user.get('cash', 0) + holdings_value)}"
            )
        )

    def refresh_market_list(self) -> None:
        category = self.filter_var.get()
        previous = self.selected_symbol.get()
        self.market_list.delete(0, END)
        self.market_change_list.delete(0, END)
        self.visible_assets = []
        for item in sorted(self.get_assets(), key=lambda x: x["symbol"]):
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
            messagebox.showerror("Invalid quantity", "Enter a numeric quantity.")
            return None
        if qty <= 0:
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
            messagebox.showerror("Not enough cash", f"Need {money(cost)}, but you have {money(user['cash'])}.")
            return
        user["cash"] = round(user["cash"] - cost, 2)
        user.setdefault("portfolio", {})[item["symbol"]] = round(user.get("portfolio", {}).get(item["symbol"], 0) + qty, 3)
        self.record_transaction("BUY", item["symbol"], qty, item["price"])
        self.status.set(f"Bought {qty:.3f} {item['symbol']} for {money(cost)}.")
        self.refresh_all()

    def sell_selected(self) -> None:
        item = self.selected_asset()
        qty = self.parse_quantity()
        if not item or qty is None:
            return
        user = self.session.user
        owned = user.get("portfolio", {}).get(item["symbol"], 0)
        if qty > owned:
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

    def tick(self) -> None:
        advance_market(self.session.market_data, ticks=1)
        self.status.set("Market tick simulated. Prices and news updated.")
        self.refresh_all()

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
        if self.live_updates_enabled:
            self.stop_live_updates()
            self.status.set("Market updates frozen. Manual ticks still work.")
        else:
            self.start_live_updates()
            self.status.set(f"Market updates resumed at {self.current_interval_seconds():.1f}s per tick.")

    def apply_live_speed(self) -> None:
        interval = self.current_interval_seconds()
        self.live_interval_seconds.set(f"{interval:g}")
        if self.live_updates_enabled:
            if self.live_update_job:
                self.root.after_cancel(self.live_update_job)
                self.live_update_job = None
            self.schedule_live_update()
        self.status.set(f"Market step speed set to {interval:.1f} seconds.")

    def current_interval_seconds(self) -> float:
        try:
            interval = float(self.live_interval_seconds.get())
        except ValueError:
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
        self.status.set(f"Live market tick. Next update in {self.current_interval_seconds():.1f}s.")
        self.refresh_all()
        self.schedule_live_update()

