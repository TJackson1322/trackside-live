"""Phase 3 parity, adversarial input, cache, and stress checks."""

import random
import unittest

from phase1_data_structures import Driver, _height
from phase2_poc import RaceSession
from phase3_optimized import OptimizedRaceSession
import test_phase2 as phase2_tests


class TestOptimizedContract(phase2_tests.TestRaceSession):
    """Run the five original integration checks on the optimized session."""

    def setUp(self):
        self.session = OptimizedRaceSession()
        self.driver = Driver("d1", "Demo Racer One", "07")
        self.session.register_driver(self.driver)


class TestPhase3(unittest.TestCase):
    def make_session(self, cls, count):
        session = cls()
        for i in range(count):
            session.register_driver(Driver(f"d{i:05}", f"Demo {i}", str(i)))
        return session

    def assert_avl(self, node, lower=None, upper=None):
        if node is None:
            return
        if lower is not None:
            self.assertLess(lower, node.key)
        if upper is not None:
            self.assertLess(node.key, upper)
        self.assertLessEqual(abs(_height(node.left) - _height(node.right)), 1)
        self.assertEqual(node.height, 1 + max(_height(node.left), _height(node.right)))
        self.assert_avl(node.left, lower, node.key)
        self.assert_avl(node.right, node.key, upper)

    def test_stream_parity_and_avl_invariants(self):
        baseline = self.make_session(RaceSession, 100)
        optimized = self.make_session(OptimizedRaceSession, 100)
        rng = random.Random(2026)
        best = {}
        for i in range(5000):
            driver_id = f"d{rng.randrange(100):05}"
            seconds = rng.randrange(1000, 3000) / 100
            baseline.record_lap(driver_id, seconds)
            optimized.record_lap(driver_id, seconds)
            best[driver_id] = min(seconds, best.get(driver_id, seconds))
            if i % 100 == 0:
                expected = sorted((time, driver) for driver, time in best.items())
                self.assertEqual(baseline.rankings(), expected)
                self.assertEqual(optimized.rankings(), expected)
                self.assertEqual(optimized.fastest_lap(), expected[0])
                self.assert_avl(optimized._leaderboard._root)
        self.assertEqual(optimized.rankings(), baseline.rankings())

    def test_cache_invalidation_and_caller_mutation(self):
        session = self.make_session(OptimizedRaceSession, 2)
        self.assertEqual(session.rankings(), [])
        session.record_lap("d00000", 18)
        snapshot = session.rankings()
        snapshot.clear()
        self.assertEqual(session.rankings(), [(18, "d00000")])
        cache = session._rankings_cache
        session.record_lap("d00000", 19)
        self.assertIs(session._rankings_cache, cache)
        session.record_lap("d00001", 17)
        self.assertIsNone(session._rankings_cache)
        self.assertEqual(session.rankings(), [(17, "d00001"), (18, "d00000")])
        session.record_lap("d00000", 16)
        self.assertEqual(session.fastest_lap(), (16, "d00000"))
        self.assertEqual(session.rankings()[0], (16, "d00000"))

    def test_ties_arriving_in_reverse_order(self):
        session = self.make_session(OptimizedRaceSession, 20)
        for i in reversed(range(20)):
            session.record_lap(f"d{i:05}", 17)
        self.assertEqual(session.fastest_lap(), (17, "d00000"))
        self.assertEqual(session.rankings(), [(17, f"d{i:05}") for i in range(20)])

    def test_adversarial_improvement_orders(self):
        for reverse in (False, True):
            session = self.make_session(OptimizedRaceSession, 1000)
            ids = list(range(1000))
            if reverse:
                ids.reverse()
            for i in ids:
                session.record_lap(f"d{i:05}", 1001 + i)
            session.rankings()
            for i in reversed(ids):
                session.record_lap(f"d{i:05}", 1 + i)
            self.assertEqual(session.rankings(), [(1 + i, f"d{i:05}") for i in range(1000)])
            self.assert_avl(session._leaderboard._root)

    def test_invalid_input_preserves_warm_cache(self):
        session = self.make_session(OptimizedRaceSession, 1)
        session.record_lap("d00000", 17)
        expected = session.rankings()
        cache = session._rankings_cache
        for seconds in (0, -1, float("nan"), float("inf"), -float("inf")):
            with self.subTest(seconds=seconds):
                with self.assertRaises(ValueError):
                    session.record_lap("d00000", seconds)
                self.assertEqual(session.rankings(), expected)
                self.assertIs(session._rankings_cache, cache)

    def test_stress_100000_laps(self):
        session = self.make_session(OptimizedRaceSession, 1000)
        for i in range(100000):
            session.record_lap(f"d{i % 1000:05}", 17 + i // 1000)
        self.assertEqual(len(session.rankings()), 1000)
        self.assertEqual(session.fastest_lap(), (17, "d00000"))
        self.assertEqual(len(session._leaderboard), 1000)
        self.assert_avl(session._leaderboard._root)


if __name__ == "__main__":
    unittest.main()
