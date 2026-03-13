from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from poker_agent import GameState, HeadsUpBettingAgent

RANKS = "23456789TJQKA"
SUITS = "cdhs"
SUIT_SYMBOLS = {"c": "\u2663", "d": "\u2666", "h": "\u2665", "s": "\u2660"}
SUIT_COLORS = {"c": "#143D2E", "d": "#B83B3B", "h": "#D1495B", "s": "#1F2937"}

TABLE_BG = "#0B3B2E"
TABLE_OUTER = "#3B2215"
FELT_DARK = "#0D5A43"
FELT_LIGHT = "#167458"
PANEL_BG = "#F7F2E8"
PANEL_ALT = "#E8DDC7"
ACCENT = "#E0B44C"
ACCENT_DARK = "#A87F24"
TEXT_DARK = "#1F1A17"
TEXT_MUTED = "#6B625B"
CARD_BORDER = "#C7B99B"
CARD_DISABLED = "#D9D1C2"


def format_card(card: str) -> str:
    return f"{card[0]}{SUIT_SYMBOLS[card[1]]}"


def action_colors(action_text: str) -> tuple[str, str]:
    if "FOLD" in action_text:
        return "#B64545", "#FFF8F5"
    if "CALL" in action_text or "CHECK" in action_text:
        return "#356FA8", "#F5FAFF"
    if "BET" in action_text or "RAISE" in action_text:
        return "#2D8A57", "#F4FFF8"
    if "ALL_IN" in action_text:
        return "#7A3DB8", "#FBF7FF"
    return ACCENT, TEXT_DARK


class CardSelector(tk.LabelFrame):
    def __init__(
        self,
        master: tk.Misc,
        title: str,
        count: int,
        on_change: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(
            master,
            text=title,
            bg=PANEL_BG,
            fg=TEXT_DARK,
            font=("Georgia", 12, "bold"),
            bd=2,
            padx=12,
            pady=12,
            relief="groove",
        )
        self.count = count
        self.on_change = on_change
        self.selected_cards: list[str] = []
        self.card_buttons: dict[str, tk.Button] = {}
        self.status_var = tk.StringVar(value=self._status_text())

        status = tk.Label(
            self,
            textvariable=self.status_var,
            bg=PANEL_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
            anchor="w",
        )
        status.grid(row=0, column=0, columnspan=14, sticky="ew", pady=(0, 10))

        self.scroll_canvas = tk.Canvas(
            self,
            bg=PANEL_BG,
            highlightthickness=0,
            height=122,
        )
        self.scroll_canvas.grid(row=1, column=0, sticky="ew")

        self.scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.scroll_canvas.xview)
        self.scrollbar.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        self.scroll_canvas.configure(xscrollcommand=self.scrollbar.set)

        self.grid_columnconfigure(0, weight=1)
        self.inner_frame = tk.Frame(self.scroll_canvas, bg=PANEL_BG)
        self.canvas_window = self.scroll_canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", self._on_inner_frame_configure)
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)

        for row_index, suit in enumerate(reversed(SUITS), start=1):
            suit_label = tk.Label(
                self.inner_frame,
                text=SUIT_SYMBOLS[suit],
                bg=PANEL_BG,
                fg=SUIT_COLORS[suit],
                font=("Segoe UI", 10, "bold"),
                width=2,
            )
            suit_label.grid(row=row_index, column=0, padx=(0, 8), pady=2)

            for column_index, rank in enumerate(RANKS, start=1):
                card = rank + suit
                button = tk.Button(
                    self.inner_frame,
                    text=self._button_text(card),
                    width=4,
                    height=1,
                    font=("Consolas", 9, "bold"),
                    bg="#FFFDF9",
                    fg=SUIT_COLORS[suit],
                    activebackground="#FFF6DA",
                    activeforeground=SUIT_COLORS[suit],
                    relief="raised",
                    bd=1,
                    cursor="hand2",
                    command=lambda current=card: self.toggle_card(current),
                )
                button.grid(row=row_index, column=column_index, padx=2, pady=2)
                self.card_buttons[card] = button

    def toggle_card(self, card: str) -> None:
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        elif len(self.selected_cards) < self.count:
            self.selected_cards.append(card)
        else:
            messagebox.showinfo("Card limit reached", f"You can only choose {self.count} card(s) here.")
            return

        self._refresh_buttons()
        if self.on_change is not None:
            self.on_change()

    def set_disabled_cards(self, cards: set[str]) -> None:
        for card, button in self.card_buttons.items():
            if card in cards and card not in self.selected_cards:
                button.configure(
                    state="disabled",
                    bg=CARD_DISABLED,
                    fg="#8D8478",
                    relief="flat",
                )
            else:
                button.configure(state="normal")
                self._apply_button_style(card)

    def get_cards(self) -> tuple[str, ...]:
        return tuple(self.selected_cards)

    def clear(self) -> None:
        self.selected_cards.clear()
        self._refresh_buttons()

    def _refresh_buttons(self) -> None:
        for card in self.card_buttons:
            self._apply_button_style(card)
        self.status_var.set(self._status_text())

    def _apply_button_style(self, card: str) -> None:
        button = self.card_buttons[card]
        selected = card in self.selected_cards
        suit = card[1]

        if selected:
            button.configure(
                text=self._button_text(card, selected=True),
                bg=ACCENT,
                fg=TEXT_DARK,
                activebackground="#F3D98B",
                activeforeground=TEXT_DARK,
                relief="sunken",
                bd=2,
            )
            return

        button.configure(
            text=self._button_text(card),
            bg="#FFFDF9",
            fg=SUIT_COLORS[suit],
            activebackground="#FFF6DA",
            activeforeground=SUIT_COLORS[suit],
            relief="raised",
            bd=1,
        )

    def _button_text(self, card: str, selected: bool = False) -> str:
        rank, suit = card[0], card[1]
        if selected:
            return f"{rank}{SUIT_SYMBOLS[suit]}*"
        return f"{rank}{SUIT_SYMBOLS[suit]}"

    def _status_text(self) -> str:
        if not self.selected_cards:
            return f"Selected: none ({len(self.selected_cards)}/{self.count})"
        return f"Selected: {'  '.join(format_card(card) for card in self.selected_cards)} ({len(self.selected_cards)}/{self.count})"

    def _on_inner_frame_configure(self, _event: tk.Event) -> None:
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self.scroll_canvas.itemconfigure(self.canvas_window, height=event.height)


class PokerAgentGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Heads-Up Poker Decision Table")
        self.root.configure(bg=TABLE_BG)
        self.root.minsize(900, 650)
        self.agent = HeadsUpBettingAgent()

        self.position_var = tk.StringVar(value="button")
        self.pot_var = tk.StringVar(value="10")
        self.to_call_var = tk.StringVar(value="0")
        self.hero_stack_var = tk.StringVar(value="100")
        self.villain_stack_var = tk.StringVar(value="100")
        self.min_raise_var = tk.StringVar(value="6")
        self.big_blind_var = tk.StringVar(value="1")

        self.result_var = tk.StringVar(value="Build the hand, set the betting state, and ask for a recommendation.")
        self.amount_var = tk.StringVar(value="Recommended amount ($): --")
        self.reason_var = tk.StringVar(value="The agent will explain the decision here.")
        self.hero_stack_display = tk.StringVar(value="Hero Stack: $100")
        self.villain_stack_display = tk.StringVar(value="Villain Stack: $100")
        self.pot_display = tk.StringVar(value="Pot: $10")

        self.outer_frame = tk.Frame(self.root, bg=TABLE_BG)
        self.outer_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.scroll_canvas = tk.Canvas(
            self.outer_frame,
            bg=TABLE_BG,
            highlightthickness=0,
        )
        self.scroll_canvas.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self.outer_frame, orient="vertical", command=self.scroll_canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.outer_frame.columnconfigure(0, weight=1)
        self.outer_frame.rowconfigure(0, weight=1)

        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.main_frame = tk.Frame(self.scroll_canvas, bg=TABLE_BG)
        self.canvas_window = self.scroll_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.main_frame.bind("<Configure>", self._on_main_frame_configure)
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self._configure_styles()
        self._build_layout()
        for variable in (
            self.pot_var,
            self.to_call_var,
            self.hero_stack_var,
            self.villain_stack_var,
            self.min_raise_var,
            self.big_blind_var,
        ):
            variable.trace_add("write", self._on_state_value_change)
        self.refresh_disabled_cards()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(
            "Sidebar.TLabelframe",
            background=PANEL_ALT,
            bordercolor=ACCENT_DARK,
            relief="groove",
        )
        style.configure(
            "Sidebar.TLabelframe.Label",
            background=PANEL_ALT,
            foreground=TEXT_DARK,
            font=("Georgia", 12, "bold"),
        )
        style.configure(
            "Poker.TLabel",
            background=PANEL_ALT,
            foreground=TEXT_DARK,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Poker.TEntry",
            fieldbackground="#FFFDF9",
            foreground=TEXT_DARK,
            bordercolor=CARD_BORDER,
            lightcolor=CARD_BORDER,
            darkcolor=CARD_BORDER,
        )
        style.configure(
            "Poker.TCombobox",
            fieldbackground="#FFFDF9",
            foreground=TEXT_DARK,
        )
        style.configure(
            "Primary.TButton",
            background=ACCENT,
            foreground=TEXT_DARK,
            font=("Segoe UI", 10, "bold"),
            padding=(14, 10),
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#F3D98B")],
            foreground=[("active", TEXT_DARK)],
        )
        style.configure(
            "Secondary.TButton",
            background="#EFE5D1",
            foreground=TEXT_DARK,
            font=("Segoe UI", 10, "bold"),
            padding=(14, 10),
        )

    def _build_layout(self) -> None:
        header = tk.Frame(self.main_frame, bg=TABLE_BG, padx=20, pady=18)
        header.grid(row=0, column=0, sticky="ew")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        title = tk.Label(
            header,
            text="Heads-Up Poker Decision Table",
            bg=TABLE_BG,
            fg="#F8F1DE",
            font=("Georgia", 24, "bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = tk.Label(
            header,
            text="Pick your cards, map the board, and size the spot like you’re at the table.",
            bg=TABLE_BG,
            fg="#D8CFAF",
            font=("Segoe UI", 11),
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(4, 0))

        content = tk.Frame(self.main_frame, bg=TABLE_BG, padx=18, pady=8)
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        left = tk.Frame(content, bg=TABLE_BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        table_shell = tk.Frame(left, bg=TABLE_OUTER, bd=4, relief="ridge", padx=16, pady=16)
        table_shell.grid(row=0, column=0, sticky="nsew", pady=(0, 14))
        table_shell.columnconfigure(0, weight=1)
        table_shell.rowconfigure(0, weight=1)

        table = tk.Frame(table_shell, bg=FELT_DARK, padx=24, pady=20)
        table.grid(row=0, column=0, sticky="nsew")
        table.columnconfigure(0, weight=1)
        table.rowconfigure(1, weight=1)

        rail = tk.Frame(table, bg=FELT_DARK)
        rail.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        rail.columnconfigure(0, weight=1)
        rail.columnconfigure(1, weight=1)

        tk.Label(
            rail,
            text="Heads-Up Table",
            bg=FELT_DARK,
            fg="#F5E8C7",
            font=("Georgia", 16, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            rail,
            text="No-limit hold'em advisor",
            bg=FELT_DARK,
            fg="#C6E3D8",
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))
        self.board_street_label = tk.Label(
            rail,
            text="Preflop",
            bg=ACCENT,
            fg=TEXT_DARK,
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=5,
        )
        self.board_street_label.grid(row=0, column=1, rowspan=2, sticky="e")

        self.table_stage = tk.Canvas(
            table,
            bg=FELT_DARK,
            highlightthickness=0,
            height=430,
        )
        self.table_stage.grid(row=1, column=0, sticky="nsew")
        self.table_stage.bind("<Configure>", self._draw_table_surface)

        self.opponent_panel = tk.Frame(self.table_stage, bg=FELT_LIGHT, padx=16, pady=12, bd=2, relief="groove")
        tk.Label(
            self.opponent_panel,
            text="Opponent",
            bg=FELT_LIGHT,
            fg="#F8F6F0",
            font=("Georgia", 12, "bold"),
        ).pack(anchor="w")
        tk.Label(
            self.opponent_panel,
            textvariable=self.villain_stack_display,
            bg=FELT_LIGHT,
            fg="#D8F3E4",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(4, 0))
        tk.Label(
            self.opponent_panel,
            text="Range hidden",
            bg=FELT_LIGHT,
            fg="#C3DED4",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(2, 0))

        self.center_panel = tk.Frame(self.table_stage, bg=FELT_DARK, padx=14, pady=10)
        self.pot_chip = tk.Label(
            self.center_panel,
            textvariable=self.pot_display,
            bg=ACCENT_DARK,
            fg="#FFF9EA",
            font=("Segoe UI", 11, "bold"),
            padx=14,
            pady=8,
            relief="ridge",
            bd=2,
        )
        self.pot_chip.pack(pady=(0, 10))
        self.board_preview = tk.Frame(self.center_panel, bg=FELT_DARK)
        self.board_preview.pack()

        self.hero_table_panel = tk.Frame(self.table_stage, bg=FELT_DARK, padx=10, pady=8)
        self.hero_preview = tk.Frame(self.hero_table_panel, bg=FELT_DARK)
        self.hero_preview.pack()

        self.table_stage.create_window(0, 0, window=self.opponent_panel, anchor="n", tags=("opponent",))
        self.table_stage.create_window(0, 0, window=self.center_panel, anchor="center", tags=("center",))
        self.table_stage.create_window(0, 0, window=self.hero_table_panel, anchor="s", tags=("hero",))

        hero_info = tk.Frame(left, bg=PANEL_BG, bd=3, relief="ridge", padx=18, pady=14)
        hero_info.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        hero_info.columnconfigure(0, weight=1)

        tk.Label(
            hero_info,
            text="Hero",
            bg=PANEL_BG,
            fg=TEXT_DARK,
            font=("Georgia", 13, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            hero_info,
            textvariable=self.hero_stack_display,
            bg=PANEL_BG,
            fg="#184D3B",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=(6, 2))
        tk.Label(
            hero_info,
            text="Your selected cards are shown on the table below the board.",
            bg=PANEL_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        ).grid(row=2, column=0, sticky="w")

        selectors_wrap = tk.Frame(left, bg=TABLE_BG)
        selectors_wrap.grid(row=2, column=0, sticky="nsew")
        selectors_wrap.columnconfigure(0, weight=1)
        selectors_wrap.columnconfigure(1, weight=1)

        self.hole_selector = CardSelector(selectors_wrap, "Hole Cards", 2, on_change=self.refresh_disabled_cards)
        self.hole_selector.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        self.flop_selector = CardSelector(selectors_wrap, "Flop", 3, on_change=self.refresh_disabled_cards)
        self.flop_selector.grid(row=0, column=1, sticky="nsew", pady=(0, 10))

        self.turn_selector = CardSelector(selectors_wrap, "Turn", 1, on_change=self.refresh_disabled_cards)
        self.turn_selector.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        self.river_selector = CardSelector(selectors_wrap, "River", 1, on_change=self.refresh_disabled_cards)
        self.river_selector.grid(row=1, column=1, sticky="nsew")

        right = tk.Frame(content, bg=TABLE_BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        controls = ttk.LabelFrame(right, text="Betting Controls", style="Sidebar.TLabelframe", padding=16)
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(3, weight=1)

        entries = [
            ("Pot Size ($)", self.pot_var, 0, 0),
            ("To Call ($)", self.to_call_var, 0, 2),
            ("Your Stack ($)", self.hero_stack_var, 1, 0),
            ("Opponent Stack ($)", self.villain_stack_var, 1, 2),
            ("Minimum Raise ($)", self.min_raise_var, 2, 0),
            ("Big Blind ($)", self.big_blind_var, 2, 2),
        ]

        for label_text, variable, row, column in entries:
            ttk.Label(controls, text=label_text, style="Poker.TLabel").grid(
                row=row, column=column, sticky="w", padx=(0, 8), pady=8
            )
            ttk.Entry(controls, textvariable=variable, width=12, style="Poker.TEntry").grid(
                row=row, column=column + 1, sticky="ew", pady=8
            )

        ttk.Label(controls, text="Position", style="Poker.TLabel").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=8)
        ttk.Combobox(
            controls,
            textvariable=self.position_var,
            values=("button", "big_blind"),
            state="readonly",
            width=12,
            style="Poker.TCombobox",
        ).grid(row=3, column=1, sticky="ew", pady=8)

        notes = tk.Label(
            controls,
            text="Tip: leave flop/turn/river empty for preflop. Enter all money values in dollars. Use To Call = 0 when checking.",
            bg=PANEL_ALT,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
            justify="left",
            wraplength=330,
        )
        notes.grid(row=4, column=0, columnspan=4, sticky="w", pady=(12, 0))

        action_bar = tk.Frame(right, bg=TABLE_BG, pady=14)
        action_bar.grid(row=1, column=0, sticky="ew")
        action_bar.columnconfigure(0, weight=1)
        action_bar.columnconfigure(1, weight=1)

        ttk.Button(action_bar, text="Recommend Action", style="Primary.TButton", command=self.recommend).grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        ttk.Button(action_bar, text="Clear Table", style="Secondary.TButton", command=self.clear_all).grid(
            row=0, column=1, sticky="ew"
        )

        result = tk.Frame(right, bg=PANEL_BG, bd=3, relief="ridge", padx=18, pady=18)
        result.grid(row=2, column=0, sticky="nsew")
        right.rowconfigure(2, weight=1)
        result.columnconfigure(0, weight=1)

        tk.Label(
            result,
            text="Agent Recommendation",
            bg=PANEL_BG,
            fg=TEXT_DARK,
            font=("Georgia", 15, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.result_badge = tk.Label(
            result,
            textvariable=self.result_var,
            bg=ACCENT,
            fg=TEXT_DARK,
            font=("Segoe UI", 11, "bold"),
            padx=12,
            pady=10,
            anchor="w",
            justify="left",
        )
        self.result_badge.grid(row=1, column=0, sticky="ew", pady=(14, 10))

        tk.Label(
            result,
            textvariable=self.amount_var,
            bg=PANEL_BG,
            fg=TEXT_DARK,
            font=("Consolas", 12, "bold"),
        ).grid(row=2, column=0, sticky="w")

        tk.Label(
            result,
            text="Reasoning",
            bg=PANEL_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=3, column=0, sticky="w", pady=(16, 4))

        tk.Label(
            result,
            textvariable=self.reason_var,
            bg=PANEL_BG,
            fg=TEXT_DARK,
            font=("Segoe UI", 10),
            justify="left",
            wraplength=360,
        ).grid(row=4, column=0, sticky="nw")

    def refresh_disabled_cards(self) -> None:
        all_cards = (
            set(self.hole_selector.get_cards())
            | set(self.flop_selector.get_cards())
            | set(self.turn_selector.get_cards())
            | set(self.river_selector.get_cards())
        )

        for selector in (
            self.hole_selector,
            self.flop_selector,
            self.turn_selector,
            self.river_selector,
        ):
            selector.set_disabled_cards(all_cards - set(selector.get_cards()))

        self._refresh_preview()

    def recommend(self) -> None:
        try:
            hole_cards = self.hole_selector.get_cards()
            if len(hole_cards) != 2:
                raise ValueError("Select exactly 2 hole cards.")

            flop_cards = self.flop_selector.get_cards()
            if flop_cards and len(flop_cards) != 3:
                raise ValueError("Select either 0 or 3 flop cards.")

            turn_cards = self.turn_selector.get_cards()
            river_cards = self.river_selector.get_cards()

            if river_cards and not turn_cards:
                raise ValueError("Select a turn card before selecting a river card.")

            community_cards = flop_cards + turn_cards + river_cards

            state = GameState(
                hole_cards=hole_cards,
                community_cards=community_cards,
                pot_size=self._parse_float(self.pot_var.get(), "pot size"),
                to_call=self._parse_float(self.to_call_var.get(), "to call"),
                hero_stack=self._parse_float(self.hero_stack_var.get(), "your stack"),
                villain_stack=self._parse_float(self.villain_stack_var.get(), "opponent stack"),
                min_raise=self._parse_float(self.min_raise_var.get(), "minimum raise"),
                big_blind=self._parse_float(self.big_blind_var.get(), "big blind"),
                position=self.position_var.get(),
            )

            decision = self.agent.decide(state)
            self.result_var.set(
                f"{state.street.title()} | {decision.action.value.upper()} | confidence {decision.confidence:.2f}"
            )
            self.amount_var.set(f"Recommended amount ($): {decision.amount:.2f}")
            self.reason_var.set(decision.reasoning)
            badge_bg, badge_fg = action_colors(decision.action.value.upper())
            self.result_badge.configure(bg=badge_bg, fg=badge_fg)
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))

    def clear_all(self) -> None:
        for selector in (
            self.hole_selector,
            self.flop_selector,
            self.turn_selector,
            self.river_selector,
        ):
            selector.clear()

        self.pot_var.set("10")
        self.to_call_var.set("0")
        self.hero_stack_var.set("100")
        self.villain_stack_var.set("100")
        self.min_raise_var.set("6")
        self.big_blind_var.set("1")
        self.position_var.set("button")
        self.result_var.set("Build the hand, set the betting state, and ask for a recommendation.")
        self.amount_var.set("Recommended amount ($): --")
        self.reason_var.set("The agent will explain the decision here.")
        self.result_badge.configure(bg=ACCENT, fg=TEXT_DARK)
        self.refresh_disabled_cards()

    def _draw_table_surface(self, event: tk.Event) -> None:
        self.table_stage.delete("felt")
        width = event.width
        height = event.height
        margin_x = 28
        margin_y = 20
        self.table_stage.create_oval(
            margin_x,
            margin_y,
            width - margin_x,
            height - margin_y,
            fill=FELT_LIGHT,
            outline="#E7C67A",
            width=4,
            tags=("felt",),
        )
        self.table_stage.create_oval(
            margin_x + 18,
            margin_y + 18,
            width - margin_x - 18,
            height - margin_y - 18,
            fill=FELT_DARK,
            outline="#2A8B68",
            width=2,
            tags=("felt",),
        )
        self.opponent_panel.update_idletasks()
        self.center_panel.update_idletasks()
        self.hero_table_panel.update_idletasks()

        opponent_height = self.opponent_panel.winfo_reqheight()
        center_height = self.center_panel.winfo_reqheight()
        hero_height = self.hero_table_panel.winfo_reqheight()

        opponent_y = margin_y + 18
        hero_y = height - margin_y - 18

        top_clear = opponent_y + opponent_height + 18
        bottom_clear = hero_y - hero_height - 18
        center_y = max(top_clear + center_height / 2, (top_clear + bottom_clear) / 2)
        center_y = min(center_y, bottom_clear - center_height / 2)

        self.table_stage.coords("opponent", width / 2, opponent_y)
        self.table_stage.coords("center", width / 2, center_y)
        self.table_stage.coords("hero", width / 2, hero_y)

    def _refresh_preview(self) -> None:
        hole = self.hole_selector.get_cards()
        community = self.flop_selector.get_cards() + self.turn_selector.get_cards() + self.river_selector.get_cards()
        self._refresh_table_state()

        self._render_preview_cards(self.hero_preview, hole, empty_slots=2)

        if not community:
            self.board_street_label.configure(text="Preflop")
            self._render_preview_cards(self.board_preview, (), empty_slots=5)
            return

        street = {3: "Flop", 4: "Turn", 5: "River"}.get(len(community), "Board")
        self.board_street_label.configure(text=street)
        self._render_preview_cards(self.board_preview, community, empty_slots=5)

    def _refresh_table_state(self) -> None:
        hero_stack = self.hero_stack_var.get().strip() or "--"
        villain_stack = self.villain_stack_var.get().strip() or "--"
        pot = self.pot_var.get().strip() or "--"
        self.hero_stack_display.set(f"Hero Stack: ${hero_stack}")
        self.villain_stack_display.set(f"Villain Stack: ${villain_stack}")
        self.pot_display.set(f"Pot: ${pot}")

    def _on_state_value_change(self, *_args: object) -> None:
        self._refresh_table_state()

    def _on_main_frame_configure(self, _event: tk.Event) -> None:
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self.scroll_canvas.itemconfigure(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event: tk.Event) -> None:
        if self.scroll_canvas.winfo_exists():
            self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _render_preview_cards(self, container: tk.Frame, cards: tuple[str, ...], empty_slots: int) -> None:
        for child in container.winfo_children():
            child.destroy()

        for index in range(empty_slots):
            if index < len(cards):
                card = cards[index]
                label = tk.Label(
                    container,
                    text=format_card(card),
                    bg="#FFFDF9",
                    fg=SUIT_COLORS[card[1]],
                    font=("Consolas", 14, "bold"),
                    width=4,
                    height=2,
                    relief="solid",
                    bd=1,
                )
            else:
                label = tk.Label(
                    container,
                    text="--",
                    bg="#EFE5D1",
                    fg=TEXT_MUTED,
                    font=("Consolas", 14, "bold"),
                    width=4,
                    height=2,
                    relief="solid",
                    bd=1,
                )
            label.grid(row=0, column=index, padx=(0, 6))

    def _parse_float(self, raw: str, label: str) -> float:
        try:
            return float(raw)
        except ValueError as error:
            raise ValueError(f"Enter a valid number for {label}.") from error


def main() -> None:
    root = tk.Tk()
    PokerAgentGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
