import sys
import unittest
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import nim  # noqa: E402


def winning_move(heaps):
    """What a perfect human plays: the same rule as the bot."""
    return nim.bot_move(heaps)


class ParseTests(unittest.TestCase):
    def test_reads_the_title_the_keys_write(self):
        title = nim.title(1, 3, 4, 2)
        self.assertEqual(title, "nim: take 3 from B (game 4, move 2)")
        self.assertEqual(nim.parse_move(title), {"heap": 1, "take": 3, "game": 4, "move": 2})
        self.assertEqual(nim.parse_move("  NIM:Take 1 from c (Game 1,move 1) "),
                         {"heap": 2, "take": 1, "game": 1, "move": 1})

    def test_rejects_anything_else(self):
        for title in ("nim: take 1 from D (game 1, move 1)", "nim: take 1 from A",
                      "nim: take one from A (game 1, move 1)", "take 1 from A (game 1, move 1)",
                      "nim: take 1 from A (game 1, move 1) please", "", None):
            self.assertIsNone(nim.parse_move(title), title)

    def test_game_issue_prefix(self):
        self.assertTrue(nim.is_game_issue("Nim : whatever"))
        self.assertFalse(nim.is_game_issue("bug: nim: take 1 from A"))


class StrategyTests(unittest.TestCase):
    def test_every_start_can_be_won_by_moving_first(self):
        for start in nim.STARTS:
            self.assertNotEqual(nim.nim_sum(start), 0, start)
            self.assertLessEqual(max(start), nim.MAX_HEAP)

    def test_bot_always_hands_back_a_zero_when_it_can(self):
        for heaps in product(range(nim.MAX_HEAP + 1), repeat=3):
            if not nim.nim_sum(heaps):
                continue
            heap, take = nim.bot_move(list(heaps))
            self.assertTrue(1 <= take <= heaps[heap])
            after = list(heaps)
            after[heap] -= take
            self.assertEqual(nim.nim_sum(after), 0, heaps)

    def test_from_a_zero_the_bot_stalls_with_one_match(self):
        self.assertEqual(nim.bot_move([1, 2, 3]), (2, 1))

    def test_mood_follows_the_nim_sum(self):
        state = nim.new_state()
        self.assertEqual(nim.bot_mood(state), "sweating")
        state["heaps"] = [1, 2, 3]
        self.assertEqual(nim.bot_mood(state), "calm")


class PlayTests(unittest.TestCase):
    def test_perfect_humans_beat_the_bot_and_the_next_game_starts(self):
        state = nim.new_state()
        issue = 0
        while state["game"] == 1:
            issue += 1
            heap, take = winning_move(state["heaps"])
            entry = nim.play(state, "alice", heap, take, issue, "t")
        self.assertEqual(entry["winner"], "humans")
        self.assertIsNone(entry["bot"])
        self.assertEqual(state["wins"], {"humans": 1, "bot": 0})
        self.assertEqual((state["game"], state["move"]), (2, 0))
        self.assertEqual(state["heaps"], list(nim.STARTS[1]))
        self.assertEqual(state["results"][-1]["winner"], "humans")
        self.assertIn("Humans win game 1", nim.reply(entry, state, "u"))

    def test_the_bot_wins_against_careless_humans(self):
        state = nim.new_state()
        issue = 0
        while state["game"] == 1:
            issue += 1
            heap = max(range(3), key=lambda i: state["heaps"][i])
            entry = nim.play(state, "bob", heap, 1, issue, "t")
        self.assertEqual(entry["winner"], "bot")
        self.assertEqual(state["wins"], {"humans": 0, "bot": 1})
        self.assertIn("The bot wins game 1", nim.reply(entry, state, "u"))

    def test_a_move_and_the_bots_answer(self):
        state = nim.new_state()  # 3, 4, 5: nim-sum 2
        entry = nim.play(state, "carol", 0, 3, 7, "t")  # 0, 4, 5: the bot takes 1 from C
        self.assertEqual(entry["bot"], [2, 1])
        self.assertEqual(state["heaps"], [0, 4, 4])
        self.assertEqual((state["move"], state["last_issue"]), (1, 7))
        self.assertEqual(state["players"], {"carol": 1})
        text = nim.reply(entry, state, "https://example.test")
        self.assertIn("You took **3 from A**, then the bot took **1 from C**", text)
        self.assertIn("back to **0**", text)

    def test_moves_from_an_old_board_or_too_big_are_refused(self):
        state = nim.new_state()
        move = nim.parse_move(nim.title(0, 1, 1, 1))
        self.assertIsNone(nim.check(state, move))
        nim.play(state, "dave", 0, 1, 1, "t")
        self.assertEqual(nim.check(state, move), "stale")
        too_big = nim.parse_move(nim.title(0, 5, 1, 2))
        self.assertEqual(nim.check(state, too_big), "illegal")
        with self.assertRaises(ValueError):
            nim.play(state, "dave", 0, 5, 2, "t")

    def test_log_is_capped(self):
        state = nim.new_state()
        for issue in range(1, nim.LOG_LIMIT + 20):
            heap = max(range(3), key=lambda i: state["heaps"][i])
            nim.play(state, "p", heap, 1, issue, "t")
        self.assertEqual(len(state["log"]), nim.LOG_LIMIT)
        self.assertEqual(state["log"][-1]["issue"], nim.LOG_LIMIT + 19)


if __name__ == "__main__":
    unittest.main()
