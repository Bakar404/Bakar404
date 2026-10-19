import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import bot  # noqa: E402
import build  # noqa: E402
import nim  # noqa: E402


def issue(number, title, login="octocat", **extra):
    return {"number": number, "title": title, "user": {"login": login},
            "created_at": "2026-01-01T00:00:00Z", **extra}


class DrainTests(unittest.TestCase):
    def setUp(self):
        tmp = Path(tempfile.mkdtemp())
        self.paths = (build.STATE, build.README, build.ASSETS)
        build.STATE, build.README, build.ASSETS = tmp / "nim.json", tmp / "README.md", tmp
        self.before = build.picture("specs", "s", 846)
        build.README.write_text(f"<p>\n{self.before}<br>\n{build.game(nim.new_state())}\n</p>\n\nafter\n")

    def tearDown(self):
        build.STATE, build.README, build.ASSETS = self.paths

    def test_plays_valid_moves_in_order_and_turns_down_the_rest(self):
        replies = bot.play([
            issue(5, nim.title(2, 1, 1, 1), "mona"),  # same board as #3, which went first
            issue(3, nim.title(0, 3, 1, 1)),  # 0 4 5, then the bot takes 1 from C: 0 4 4
            issue(4, "nim: take all of them"),
            issue(6, nim.title(0, 1, 1, 2), "mona"),  # heap A is empty now
            issue(7, nim.title(1, 2, 1, 2), "dependabot[bot]"),
            issue(8, nim.title(1, 2, 1, 2), "mona"),  # 0 2 4, the bot takes 2 from C: 0 2 2
            issue(9, "unrelated"),
            issue(10, nim.title(1, 1, 1, 3), pull_request={}),
        ], "https://example.test")
        self.assertEqual([(r["issue"], r["reason"]) for r in replies],
                         [(3, "completed"), (4, "not_planned"), (5, "not_planned"),
                          (6, "not_planned"), (7, "not_planned"), (8, "completed")])
        self.assertIn("Someone moved first", replies[2]["body"])
        self.assertIn("doesn't have that many", replies[3]["body"])
        state = build.load_state()
        self.assertEqual([e["issue"] for e in state["log"]], [3, 8])
        self.assertEqual((state["move"], state["heaps"]), (2, [0, 2, 2]))

        readme = build.README.read_text()
        self.assertTrue(readme.startswith(f"<p>\n{self.before}<br>\n<!-- game -->\n"))
        self.assertTrue(readme.endswith("<!-- /game -->\n</p>\n\nafter\n"))
        for name in ("board-phone", "board-dark", "board-light"):
            self.assertIn(f"assets/{name}.svg?v=1-2", readme)
            self.assertTrue((build.ASSETS / f"{name}.svg").exists())
        # keys for the legal moves only, each opening the next move of this game
        self.assertIn("assets/empty-light.svg", readme)
        self.assertEqual(readme.count("assets/take-1-light.svg"), 2)
        self.assertEqual(readme.count("assets/take-2-light.svg"), 2)
        self.assertNotIn("assets/take-3-light.svg", readme)
        self.assertIn("title=nim%3A+take+2+from+C+%28game+1%2C+move+3%29", readme)

    def test_rerun_after_a_failed_reply_does_not_replay(self):
        issues = [issue(3, nim.title(0, 1, 1, 1)), issue(4, "nim: nope"),
                  issue(5, nim.title(2, 1, 1, 2), "mona")]
        first = bot.play(issues, "u")
        second = bot.play(issues, "u")
        self.assertEqual(first, second)
        self.assertEqual(build.load_state()["move"], 2)


if __name__ == "__main__":
    unittest.main()
