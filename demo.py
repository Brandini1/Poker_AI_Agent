from __future__ import annotations

from poker_agent import GameState, HeadsUpBettingAgent


def prompt_text(label: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    value = input(f"{label}{suffix}: ").strip()
    if value:
        return value
    return "" if default is None else default


def prompt_float(label: str, default: float) -> float:
    while True:
        raw = prompt_text(label, f"{default}")
        try:
            return float(raw)
        except ValueError:
            print("Enter a number like 10 or 10.5.")


def parse_cards(raw: str, expected: int | None = None) -> tuple[str, ...]:
    if not raw.strip():
        cards: tuple[str, ...] = ()
    else:
        tokens = raw.replace(",", " ").split()
        cards = tuple(token[0].upper() + token[1].lower() for token in tokens)

    if expected is not None and len(cards) != expected:
        raise ValueError(f"Expected {expected} cards, got {len(cards)}.")
    return cards


def build_community_cards(flop: tuple[str, ...], turn: tuple[str, ...], river: tuple[str, ...]) -> tuple[str, ...]:
    community_cards = flop
    if turn:
        community_cards += turn
    if river:
        community_cards += river
    return community_cards


def collect_state() -> GameState:
    while True:
        try:
            hole_cards = parse_cards(prompt_text("Enter your two hole cards", "Ah Kd"), expected=2)
            flop = parse_cards(prompt_text("Enter flop cards or leave blank", ""), expected=None)
            if flop and len(flop) != 3:
                raise ValueError("Flop must be exactly 3 cards.")
            turn = parse_cards(prompt_text("Enter turn card or leave blank", ""), expected=None)
            if turn and len(turn) != 1:
                raise ValueError("Turn must be exactly 1 card.")
            river = parse_cards(prompt_text("Enter river card or leave blank", ""), expected=None)
            if river and len(river) != 1:
                raise ValueError("River must be exactly 1 card.")

            if river and not turn:
                raise ValueError("Enter the turn card before the river.")

            community_cards = build_community_cards(flop, turn, river)
            return GameState(
                hole_cards=hole_cards,
                community_cards=community_cards,
                pot_size=prompt_float("Current pot size", 10.0),
                to_call=prompt_float("Amount you must call (0 if checking)", 0.0),
                hero_stack=prompt_float("Your remaining stack", 100.0),
                villain_stack=prompt_float("Opponent remaining stack", 100.0),
                min_raise=prompt_float("Minimum raise amount", 6.0),
                big_blind=prompt_float("Big blind", 1.0),
                position=prompt_text("Position", "button"),
            )
        except ValueError as error:
            print(f"Input error: {error}")
            print("Please try again.\n")


def show_decision(agent: HeadsUpBettingAgent, state: GameState) -> None:
    decision = agent.decide(state)
    print("\nRecommendation")
    print(f"Street: {state.street}")
    print(f"Action: {decision.action.value}")
    print(f"Recommended amount: {decision.amount:.2f}")
    print(f"Confidence: {decision.confidence:.2f}")
    print(f"Why: {decision.reasoning}")


if __name__ == "__main__":
    print("Heads-up Poker Betting Agent")
    print("Enter cards like 'Ah Kd', flop like 'Qs Jc 2h', and leave streets blank if not dealt yet.\n")

    agent = HeadsUpBettingAgent()

    while True:
        game_state = collect_state()
        show_decision(agent, game_state)

        again = prompt_text("\nAnalyze another spot? (y/n)", "y").lower()
        if again not in {"y", "yes"}:
            break
