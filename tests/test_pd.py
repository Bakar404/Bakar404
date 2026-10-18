import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pd  # noqa: E402


class ParseTests(unittest.TestCase):
    def test_accepts_moves_case_insensitively(self):
        self.assertEqual(pd.parse_move("pd: cooperate"), "C")
        self.assertEqual(pd.parse_move("  PD:Defect "), "D")

    def test_rejects_anything_else(self):
        for title in ("pd: cooperate please", "pd: c", "cooperate", "", None, "pd:"):
            self.assertIsNone(pd.parse_move(title), title)

    def test_game_issue_prefix(self):
        self.assertTrue(pd.is_game_issue("Pd : whatever"))
        self.assertFalse(pd.is_game_issue("bug: pd: cooperate"))


class BotTests(unittest.TestCase):
    def test_opens_by_cooperating(self):
        self.assertEqual(pd.bot_move(pd.new_state(), "alice"), ("C", "opening"))

    def test_strangers_get_the_previous_players_move(self):
        state = pd.new_state()
        pd.play(state, "alice", "D", 1, "t")
        self.assertEqual(pd.bot_move(state, "bob"), ("D", "stranger"))

    def test_returning_players_get_tit_for_tat(self):
        state = pd.new_state()
        pd.play(state, "alice", "C", 1, "t")
        pd.play(state, "bob", "D", 2, "t")
        self.assertEqual(pd.bot_move(state, "alice"), ("C", "tit-for-tat"))
        self.assertEqual(pd.bot_move(state, "bob"), ("D", "tit-for-tat"))

    def test_bot_cannot_peek_at_the_current_move(self):
        state = pd.new_state()
        entry = pd.play(state, "alice", "D", 1, "t")
        self.assertEqual(entry["bot"], "C")


class PlayTests(unittest.TestCase):
    def test_scores_and_counters(self):
        state = pd.new_state()
        pd.play(state, "alice", "D", 7, "t")  # bot C -> 5,0
        pd.play(state, "bob", "C", 9, "t")    # stranger: bot D -> 0,5
        pd.play(state, "alice", "C", 8, "t")  # tit-for-tat: bot D -> 0,5
        self.assertEqual(state["round"], 3)
        self.assertEqual(state["totals"], {"humans": 5, "bot": 10})
        self.assertEqual(state["outcomes"], {"CC": 0, "CD": 2, "DC": 1, "DD": 0})
        self.assertEqual(state["last_issue"], 9)
        self.assertEqual(state["players"]["alice"], {"last": "C", "rounds": 2, "points": 5})
        self.assertEqual(pd.cooperation_rate(state), 67)
        self.assertEqual(pd.bot_mood(state), "trusting")

    def test_history_is_capped(self):
        state = pd.new_state()
        for i in range(pd.HISTORY_LIMIT + 5):
            pd.play(state, "p", "C", i + 1, "t")
        self.assertEqual(len(state["history"]), pd.HISTORY_LIMIT)
        self.assertEqual(state["history"][0]["round"], 6)

    def test_reply_explains_the_round(self):
        state = pd.new_state()
        pd.play(state, "alice", "D", 1, "t")
        entry = pd.play(state, "bob", "C", 2, "t")
        text = pd.reply(entry, state, "https://example.test")
        self.assertIn("you **cooperated**, the bot **defected**", text)
        self.assertIn("previous player **defected**", text)
        self.assertIn("**0, 5** (this round)", text)


if __name__ == "__main__":
    unittest.main()
