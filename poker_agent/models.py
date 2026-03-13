from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Action(str, Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"


@dataclass(frozen=True)
class GameState:
    hole_cards: tuple[str, str]
    community_cards: tuple[str, ...] = ()
    pot_size: float = 0.0
    to_call: float = 0.0
    hero_stack: float = 100.0
    villain_stack: float = 100.0
    min_raise: float = 0.0
    big_blind: float = 1.0
    position: str = "button"

    @property
    def street(self) -> str:
        board_cards = len(self.community_cards)
        if board_cards == 0:
            return "preflop"
        if board_cards == 3:
            return "flop"
        if board_cards == 4:
            return "turn"
        if board_cards == 5:
            return "river"
        raise ValueError("Community cards must be 0, 3, 4, or 5 cards.")


@dataclass(frozen=True)
class BettingDecision:
    action: Action
    amount: float = 0.0
    confidence: float = 0.0
    reasoning: str = ""
