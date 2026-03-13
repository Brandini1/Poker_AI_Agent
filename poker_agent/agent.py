from __future__ import annotations

from dataclasses import replace

from .evaluator import canonical_starting_hand, monte_carlo_equity
from .models import Action, BettingDecision, GameState

PREMIUM_HANDS = {
    "AA",
    "KK",
    "QQ",
    "JJ",
    "AKs",
    "AQs",
    "AKo",
}
STRONG_HANDS = PREMIUM_HANDS | {
    "TT",
    "99",
    "88",
    "AJs",
    "ATs",
    "KQs",
    "AQo",
    "AJo",
    "KQo",
    "QJs",
}
PLAYABLE_HANDS = STRONG_HANDS | {
    "77",
    "66",
    "55",
    "44",
    "33",
    "22",
    "A9s",
    "A8s",
    "KJs",
    "KTs",
    "QTs",
    "JTs",
    "T9s",
    "98s",
    "87s",
    "76s",
    "65s",
    "54s",
    "ATo",
    "KJo",
    "QJo",
    "JTo",
}


class HeadsUpBettingAgent:
    def __init__(self, simulations: int = 1200, seed: int = 7) -> None:
        self.simulations = simulations
        self.seed = seed

    def decide(self, state: GameState) -> BettingDecision:
        state = replace(
            state,
            hole_cards=tuple(self._normalize_card(card) for card in state.hole_cards),
            community_cards=tuple(self._normalize_card(card) for card in state.community_cards),
        )

        if state.street == "preflop":
            return self._decide_preflop(state)
        return self._decide_postflop(state)

    def _decide_preflop(self, state: GameState) -> BettingDecision:
        hand = canonical_starting_hand(*state.hole_cards)
        pressure = self._pot_odds(state)

        if hand in PREMIUM_HANDS:
            return self._value_action(state, 0.75, f"{hand} is a premium heads-up hand.")

        if hand in STRONG_HANDS:
            if state.to_call > 0 and pressure > 0.35:
                return BettingDecision(
                    action=Action.CALL,
                    amount=min(state.to_call, state.hero_stack),
                    confidence=0.74,
                    reasoning=f"{hand} performs well heads-up but large pressure makes calling better than inflating the pot.",
                )
            return self._value_action(state, 0.6, f"{hand} is strong enough to attack preflop heads-up.")

        if hand in PLAYABLE_HANDS:
            if state.to_call == 0:
                return BettingDecision(
                    action=Action.BET,
                    amount=self._open_size(state, 0.45),
                    confidence=0.62,
                    reasoning=f"{hand} is a profitable heads-up open from a wide range.",
                )
            if pressure <= 0.22:
                return BettingDecision(
                    action=Action.CALL,
                    amount=min(state.to_call, state.hero_stack),
                    confidence=0.58,
                    reasoning=f"{hand} can defend versus a small heads-up raise.",
                )
            return BettingDecision(
                action=Action.FOLD,
                confidence=0.57,
                reasoning=f"{hand} is playable, but the price is too poor for a profitable defense.",
            )

        if state.to_call == 0:
            return BettingDecision(
                action=Action.CHECK,
                confidence=0.55,
                reasoning=f"{hand} is near the bottom of a heads-up range, so checking is fine when no bet is required.",
            )
        if pressure <= 0.1 and self._is_suited_connector(hand):
            return BettingDecision(
                action=Action.CALL,
                amount=min(state.to_call, state.hero_stack),
                confidence=0.51,
                reasoning=f"{hand} can peel cheaply thanks to connected, suited playability.",
            )
        return BettingDecision(
            action=Action.FOLD,
            confidence=0.64,
            reasoning=f"{hand} is too weak to continue profitably versus a bet.",
        )

    def _decide_postflop(self, state: GameState) -> BettingDecision:
        equity = monte_carlo_equity(
            state.hole_cards,
            state.community_cards,
            iterations=self.simulations,
            seed=self.seed + len(state.community_cards),
        )
        pressure = self._pot_odds(state)

        if state.to_call == 0:
            if equity >= 0.78:
                return BettingDecision(
                    action=Action.BET,
                    amount=self._bet_size_from_equity(state, equity, aggressive=True),
                    confidence=min(0.95, equity),
                    reasoning=f"Estimated equity is {equity:.0%}, so betting for value is best.",
                )
            if equity >= 0.56:
                return BettingDecision(
                    action=Action.BET,
                    amount=self._bet_size_from_equity(state, equity, aggressive=False),
                    confidence=equity,
                    reasoning=f"Estimated equity is {equity:.0%}, which supports a value/protection bet.",
                )
            if equity >= 0.34:
                return BettingDecision(
                    action=Action.CHECK,
                    confidence=1 - abs(0.5 - equity),
                    reasoning=f"Estimated equity is {equity:.0%}; checking controls the pot with a marginal hand.",
                )
            return BettingDecision(
                action=Action.BET,
                amount=self._bet_size_from_equity(state, equity, aggressive=False, bluff=True),
                confidence=max(0.35, 1 - equity),
                reasoning=f"Estimated equity is {equity:.0%}; a small bluff can pressure capped one-opponent ranges.",
            )

        if equity >= 0.82:
            return self._jam_or_raise(state, equity, "Very high equity justifies a value raise or stack-off.")
        if equity >= max(pressure + 0.12, 0.55):
            return BettingDecision(
                action=Action.CALL,
                amount=min(state.to_call, state.hero_stack),
                confidence=equity,
                reasoning=f"Estimated equity is {equity:.0%}, comfortably above the pot-odds threshold of {pressure:.0%}.",
            )
        if equity >= max(pressure, 0.24) and state.street in {"flop", "turn"}:
            return BettingDecision(
                action=Action.CALL,
                amount=min(state.to_call, state.hero_stack),
                confidence=0.52,
                reasoning=f"Estimated equity is {equity:.0%}; the draw and price justify continuing for one street.",
            )
        return BettingDecision(
            action=Action.FOLD,
            confidence=max(0.55, 1 - equity),
            reasoning=f"Estimated equity is {equity:.0%}, which is not enough against the current price.",
        )

    def _value_action(self, state: GameState, sizing_factor: float, reasoning: str) -> BettingDecision:
        if state.to_call == 0:
            return BettingDecision(
                action=Action.BET,
                amount=self._open_size(state, sizing_factor),
                confidence=0.8,
                reasoning=reasoning,
            )
        raise_amount = max(state.min_raise, state.to_call * 2.5, state.big_blind * 3)
        commit = state.to_call + raise_amount
        if commit >= state.hero_stack * 0.8:
            return BettingDecision(
                action=Action.ALL_IN,
                amount=state.hero_stack,
                confidence=0.85,
                reasoning=reasoning,
            )
        return BettingDecision(
            action=Action.RAISE,
            amount=min(commit, state.hero_stack),
            confidence=0.8,
            reasoning=reasoning,
        )

    def _jam_or_raise(self, state: GameState, equity: float, reasoning: str) -> BettingDecision:
        total_commit = state.to_call + max(state.min_raise, state.pot_size * 0.8, state.big_blind * 3)
        if total_commit >= state.hero_stack * 0.7:
            return BettingDecision(
                action=Action.ALL_IN,
                amount=state.hero_stack,
                confidence=min(0.97, equity),
                reasoning=reasoning,
            )
        return BettingDecision(
            action=Action.RAISE,
            amount=min(total_commit, state.hero_stack),
            confidence=min(0.94, equity),
            reasoning=reasoning,
        )

    def _open_size(self, state: GameState, factor: float) -> float:
        baseline = max(state.big_blind * 2.5, state.pot_size * factor)
        return round(min(baseline, state.hero_stack), 2)

    def _bet_size_from_equity(
        self,
        state: GameState,
        equity: float,
        aggressive: bool,
        bluff: bool = False,
    ) -> float:
        if bluff:
            size = state.pot_size * 0.33
        elif aggressive:
            size = state.pot_size * 0.8
        else:
            size = state.pot_size * 0.55
        if state.street == "river" and not bluff and equity > 0.9:
            size = state.pot_size
        return round(min(max(size, state.big_blind), state.hero_stack), 2)

    def _pot_odds(self, state: GameState) -> float:
        if state.to_call <= 0:
            return 0.0
        return state.to_call / (state.pot_size + state.to_call)

    def _is_suited_connector(self, hand: str) -> bool:
        return len(hand) == 3 and hand[2] == "s" and abs(
            "23456789TJQKA".index(hand[0]) - "23456789TJQKA".index(hand[1])
        ) == 1

    def _normalize_card(self, card: str) -> str:
        card = card.strip()
        if len(card) != 2:
            return card
        return card[0].upper() + card[1].lower()
