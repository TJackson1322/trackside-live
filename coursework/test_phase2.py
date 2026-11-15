"""Verify the Phase 2 workflow and input handling."""

import unittest

from phase2_poc import Driver, RaceSession


class TestRaceSession(unittest.TestCase):
    def setUp(self):
        self.session = RaceSession()
        self.driver = Driver("d1", "Demo Racer One", "07")
        self.session.register_driver(self.driver)

    def test_lookup_and_empty_results(self):
        self.assertEqual(self.session.find_driver("d1"), self.driver)
        self.assertIsNone(self.session.find_driver("unknown"))
        self.assertIsNone(self.session.fastest_lap())
        self.assertEqual(self.session.rankings(), [])

    def test_update_only_when_lap_is_faster(self):
        self.session.register_driver(Driver("d2", "Demo Racer Two", "88"))
        self.session.record_lap("d1", 17.45)
        self.session.record_lap("d2", 17.21)
        self.session.record_lap("d2", 17.80)
        self.assertEqual(self.session.rankings(), [(17.21, "d2"), (17.45, "d1")])
        self.session.record_lap("d1", 17.10)
        self.assertEqual(self.session.fastest_lap(), (17.10, "d1"))
        self.assertEqual(self.session.rankings(), [(17.10, "d1"), (17.21, "d2")])

    def test_tie_and_repeat_lap_keep_one_ranking_per_driver(self):
        self.session.register_driver(Driver("d2", "Demo Racer Two", "88"))
        for driver_id in ("d2", "d1", "d2"):
            self.session.record_lap(driver_id, 17.0)
        self.assertEqual(self.session.fastest_lap(), (17.0, "d1"))
        self.assertEqual(self.session.rankings(), [(17.0, "d1"), (17.0, "d2")])

    def test_invalid_laps_leave_results_unchanged(self):
        self.session.record_lap("d1", 17.5)
        for driver_id, seconds in [
            ("unknown", 1.0),
            ("d1", 0.0),
            ("d1", -1.0),
            ("d1", float("inf")),
            ("d1", float("nan")),
        ]:
            with self.subTest(driver_id=driver_id, seconds=seconds):
                with self.assertRaises(ValueError):
                    self.session.record_lap(driver_id, seconds)
                self.assertEqual(self.session.fastest_lap(), (17.5, "d1"))
                self.assertEqual(self.session.rankings(), [(17.5, "d1")])

    def test_reject_duplicate_and_blank_driver_ids(self):
        with self.assertRaises(ValueError):
            self.session.register_driver(Driver("d1", "Duplicate", "00"))
        with self.assertRaises(ValueError):
            self.session.register_driver(Driver(" ", "Blank ID", "00"))
        self.assertEqual(self.session.find_driver("d1"), self.driver)


if __name__ == "__main__":
    unittest.main()
