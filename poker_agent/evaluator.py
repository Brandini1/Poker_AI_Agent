from __future__ import annotations

from itertools import combinations
from random import Random

RANKS = "23456789TJQKA"
SUITS = "cdhs"
RANK_VALUE = {rank: index + 2 for index, rank in enumerate(RANKS)}


def card_rank(card: str) -> str:
    normalized = _normalize_card(card)
    return normalized[0]


def card_suit(card: str) -> str:
    normalized = _normalize_card(card)
    return normalized[1]


def canonical_starting_hand(card1: str, card2: str) -> str:
    rank1 = card_rank(card1)
    rank2 = card_rank(card2)
    if rank1 == rank2:
        return rank1 + rank2

    high, low = sorted((rank1, rank2), key=lambda rank: RANK_VALUE[rank], reverse=True)
    suited = "s" if card_suit(card1) == card_suit(card2) else "o"
    return f"{high}{low}{suited}"


def full_deck() -> list[str]:
    return [rank + suit for rank in RANKS for suit in SUITS]


def monte_carlo_equity(
    hole_cards: tuple[str, str],
    community_cards: tuple[str, ...],
    opponents: int = 1,
    iterations: int = 1200,
    seed: int = 7,
) -> float:
    if opponents != 1:
        raise ValueError("This evaluator currently supports heads-up only.")

    known_cards = set(hole_cards) | set(community_cards)
    if len(known_cards) != len(hole_cards) + len(community_cards):
        raise ValueError("Duplicate cards found in game state.")

    deck = [card for card in full_deck() if card not in known_cards]
    board_missing = 5 - len(community_cards)
    rng = Random(seed)

    wins = 0.0
    for _ in range(iterations):
        sample = rng.sample(deck, 2 + board_missing)
        villain_hole = tuple(sample[:2])
        runout = tuple(sample[2:])
        final_board = tuple(community_cards) + runout

        hero_score = best_hand_score(hole_cards + final_board)
        villain_score = best_hand_score(villain_hole + final_board)

        if hero_score > villain_score:
            wins += 1.0
        elif hero_score == villain_score:
            wins += 0.5

    return wins / iterations


def best_hand_score(cards: tuple[str, ...]) -> tuple[int, tuple[int, ...]]:
    if len(cards) < 5:
        raise ValueError("At least five cards are required to score a hand.")
    return max(_score_five_card_hand(combo) for combo in combinations(cards, 5))


def _score_five_card_hand(cards: tuple[str, ...]) -> tuple[int, tuple[int, ...]]:
    ranks = sorted((RANK_VALUE[card_rank(card)] for card in cards), reverse=True)
    suits = [card_suit(card) for card in cards]
    counts = {rank: ranks.count(rank) for rank in set(ranks)}
    ordered = sorted(counts.items(), key=lambda item: (item[1], item[0]), reverse=True)
    is_flush = len(set(suits)) == 1
    straight_high = _straight_high(ranks)

    if is_flush and straight_high:
        return 8, (straight_high,)
    if ordered[0][1] == 4:
        four = ordered[0][0]
        kicker = max(rank for rank in ranks if rank != four)
        return 7, (four, kicker)
    if ordered[0][1] == 3 and ordered[1][1] == 2:
        return 6, (ordered[0][0], ordered[1][0])
    if is_flush:
        return 5, tuple(ranks)
    if straight_high:
        return 4, (straight_high,)
    if ordered[0][1] == 3:
        trips = ordered[0][0]
        kickers = tuple(rank for rank in ranks if rank != trips)
        return 3, (trips,) + kickers
    if ordered[0][1] == 2 and ordered[1][1] == 2:
        pair_high = max(ordered[0][0], ordered[1][0])
        pair_low = min(ordered[0][0], ordered[1][0])
        kicker = max(rank for rank in ranks if rank not in (pair_high, pair_low))
        return 2, (pair_high, pair_low, kicker)
    if ordered[0][1] == 2:
        pair = ordered[0][0]
        kickers = tuple(rank for rank in ranks if rank != pair)
        return 1, (pair,) + kickers
    return 0, tuple(ranks)


def _straight_high(ranks: list[int]) -> int:
    unique = sorted(set(ranks), reverse=True)
    if 14 in unique:
        unique.append(1)
    for index in range(len(unique) - 4):
        window = unique[index : index + 5]
        if window[0] - window[4] == 4 and len(window) == 5:
            return window[0]
    return 0


def _validate_card(card: str) -> None:
    _normalize_card(card)


def _normalize_card(card: str) -> str:
    card = card.strip()
    if len(card) != 2 or card[0] not in RANKS or card[1] not in SUITS:
        if len(card) == 2 and card[0].upper() in RANKS and card[1].lower() in SUITS:
            return card[0].upper() + card[1].lower()
        raise ValueError(f"Invalid card: {card}")
    return card[0] + card[1]
