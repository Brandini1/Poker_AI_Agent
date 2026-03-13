import unittest

from poker_agent import Action, GameState, HeadsUpBettingAgent


class HeadsUpBettingAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = HeadsUpBettingAgent(simulations=400, seed=11)

    def test_premium_preflop_hand_is_aggressive(self) -> None:
        decision = self.agent.decide(
            GameState(
                hole_cards=("As", "Ad"),
                pot_size=1.5,
                to_call=1.5,
                hero_stack=100,
                villain_stack=100,
                min_raise=3.0,
                big_blind=1.0,
            )
        )
        self.assertIn(decision.action, {Action.RAISE, Action.ALL_IN})

    def test_weak_preflop_hand_folds_to_pressure(self) -> None:
        decision = self.agent.decide(
            GameState(
                hole_cards=("7d", "2c"),
                pot_size=4.0,
                to_call=3.0,
                hero_stack=100,
                villain_stack=100,
                min_raise=6.0,
                big_blind=1.0,
            )
        )
        self.assertEqual(decision.action, Action.FOLD)

    def test_nut_flush_draw_continues_on_flop(self) -> None:
        decision = self.agent.decide(
            GameState(
                hole_cards=("Ah", "Kh"),
                community_cards=("Qh", "7h", "2c"),
                pot_size=10.0,
                to_call=3.0,
                hero_stack=90,
                villain_stack=90,
                min_raise=6.0,
                big_blind=1.0,
            )
        )
        self.assertIn(decision.action, {Action.CALL, Action.RAISE, Action.ALL_IN})

    def test_river_air_folds_to_large_bet(self) -> None:
        decision = self.agent.decide(
            GameState(
                hole_cards=("9c", "8d"),
                community_cards=("As", "Kd", "Qh", "2c", "2d"),
                pot_size=20.0,
                to_call=16.0,
                hero_stack=60,
                villain_stack=60,
                min_raise=32.0,
                big_blind=1.0,
            )
        )
        self.assertEqual(decision.action, Action.FOLD)


if __name__ == "__main__":
    unittest.main()
