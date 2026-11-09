import re
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


class ProjectTests(unittest.TestCase):
    def test_titles_fit_their_cards_at_both_sizes(self):
        desktop = scenes.W // 2 - scenes.CARD_GAP // 2 - 8 - 2 * 16 - text_width("→", 2, True) - 8
        phone = scenes.M // 2 - 12 // 2 - 8 - 2 * 12
        for _, title, *_ in scenes.PROJECTS:
            with self.subTest(title=title):
                self.assertLessEqual(text_width(title, 2, True), desktop)
                for word in title.split():
                    self.assertLessEqual(text_width(word, 2, True), phone)

    def test_cards_in_a_layout_share_one_height(self):
        for render in (lambda i: scenes.project_card(i, "light"), scenes.project_card_mobile):
            heights = {re.search(r'height="(\d+)"', render(i)).group(1)
                       for i in range(len(scenes.PROJECTS))}
            self.assertEqual(len(heights), 1)

    def test_readme_links_every_project_and_link(self):
        import build
        readme = (build.ROOT / "README.md").read_text()
        for repo, *_ in scenes.PROJECTS:
            self.assertIn(f'href="https://github.com/{build.OWNER}/{repo}"', readme)
        for _, url in scenes.LINKS:
            self.assertIn(url, readme)


if __name__ == "__main__":
    unittest.main()
