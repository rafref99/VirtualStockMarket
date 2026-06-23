from __future__ import annotations

from tkinter import Tk
from tkinter import ttk

from ui import VirtualStockMarketApp


def main() -> None:
    root = Tk()
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")
    VirtualStockMarketApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
