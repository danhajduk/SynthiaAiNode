import unittest

from ai_node.main import run


class MainEntrypointTests(unittest.TestCase):
    def test_run_once_returns_success(self):
        rc = run(once=True, interval_seconds=0.01)
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
