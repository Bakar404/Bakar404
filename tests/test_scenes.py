import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import nim  # noqa: E402
import scenes  # noqa: E402
from pixel import text_width  # noqa: E402

ROOM, PHONE_ROOM = scenes.W - 2 * scenes.PAD, scenes.M - 2 * scenes.MPAD


def ended(login: str, winner: str | None) -> dict:
    state = nim.new_state()
    state["log"] = [{"player": login, "game": 12, "heap": 2, "take": 5, "winner": winner,
                     "bot": {None: [1, 5], "humans": None, "bot": [0, 5]}[winner]}]
    return state


class LastMoveTests(unittest.TestCase):
    def phone_lines(self, state: dict) -> list[str]:
        label, lines = scenes.last_move_mobile(state, PHONE_ROOM)
        for line in lines:
            self.assertLessEqual(scenes.log_indent(label) + text_width(line, 2), PHONE_ROOM)
        return lines

    def test_fits_on_the_board_with_the_longest_login(self):
        login = "W" * 39  # GitHub's longest login, in the font's widest letter
        for winner in (None, "humans", "bot"):
            with self.subTest(winner=winner):
                state = ended(login, winner)
                self.assertLessEqual(scenes.runs_width(scenes.last_move(state, ROOM), 2), ROOM)
                self.phone_lines(state)

    def test_shows_an_ordinary_login_in_full(self):
        for login in ("octocat", "mona-lisa-octocat-42"):
            for winner in (None, "humans"):
                with self.subTest(login=login, winner=winner):
                    state = ended(login, winner)
                    desktop = " ".join(t for t, _, _ in scenes.last_move(state, ROOM))
                    self.assertIn(f"@{login}", desktop)
                    self.assertIn(f"@{login}", " ".join(self.phone_lines(state)))


if __name__ == "__main__":
    unittest.main()
