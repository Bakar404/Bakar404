import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import bot  # noqa: E402
import build  # noqa: E402
import pd  # noqa: E402


def issue(number, title, login="octocat", **extra):
    return {"number": number, "title": title, "user": {"login": login},
            "created_at": "2026-01-01T00:00:00Z", **extra}


class DrainTests(unittest.TestCase):
    def setUp(self):
        tmp = Path(tempfile.mkdtemp())
        self.paths = (build.STATE, build.README, build.ASSETS)
        build.STATE, build.README, build.ASSETS = tmp / "pd.json", tmp / "README.md", tmp
        self.tagline = build.picture("tagline", "t", 846)
        build.README.write_text(f"{self.tagline}<br>\n{build.board_picture(pd.new_state())}<br>\ny\n")

    def tearDown(self):
        build.STATE, build.README, build.ASSETS = self.paths

    def test_plays_valid_moves_in_order_and_rejects_the_rest(self):
        replies = bot.play([
            issue(5, "pd: defect", "mona"),
            issue(3, "pd: cooperate"),
            issue(4, "pd: maybe"),
            issue(6, "pd: cooperate", "dependabot[bot]"),
            issue(7, "unrelated"),
            issue(8, "pd: cooperate", pull_request={}),
        ], "https://example.test")
        self.assertEqual([(r["issue"], r["reason"]) for r in replies],
                         [(3, "completed"), (4, "not_planned"), (5, "completed"),
                          (6, "not_planned")])
        state = build.load_state()
        self.assertEqual([e["issue"] for e in state["history"]], [3, 5])
        readme = build.README.read_text()
        for name in ("board-phone", "board-dark", "board-light"):
            self.assertIn(f"assets/{name}.svg?r=2", readme)
            self.assertTrue((build.ASSETS / f"{name}.svg").exists())
        self.assertTrue(readme.startswith(self.tagline))
        self.assertEqual(readme.count("<picture>"), 2)

    def test_rerun_after_a_failed_reply_does_not_replay(self):
        issues = [issue(3, "pd: cooperate"), issue(4, "pd: nope"), issue(5, "pd: defect", "mona")]
        first = bot.play(issues, "u")
        second = bot.play(issues, "u")
        self.assertEqual(first, second)
        self.assertEqual(build.load_state()["round"], 2)


if __name__ == "__main__":
    unittest.main()
