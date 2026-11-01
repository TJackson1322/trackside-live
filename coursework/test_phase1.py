"""Unit tests for the independent academic data structures."""
import unittest
from phase1_data_structures import Driver, DriverIndex, FastestLaps, LeaderboardAVL


class TestPhase1(unittest.TestCase):
    def test_hash_lookup(self):
        index = DriverIndex()
        index.add(Driver("a", "Racer", "07"))
        self.assertEqual(index.find("a").name, "Racer")
        self.assertIsNone(index.find("missing"))

    def test_heap(self):
        laps = FastestLaps()
        laps.add("a", 18.2)
        laps.add("b", 17.5)
        self.assertEqual(laps.fastest(), (17.5, "b"))
        self.assertEqual(laps.pop_fastest(), (17.5, "b"))
        with self.assertRaises(ValueError):
            laps.add("x", -1)

    def test_avl_update_remove_and_sort(self):
        board = LeaderboardAVL()
        for i in range(100):
            board.update(str(i), float(100-i))
        self.assertEqual(board.rankings(), sorted(board.rankings()))
        board.update("99", 101.0)
        self.assertEqual(board.rankings()[-1], (101.0, "99"))
        self.assertTrue(board.remove("50"))
        self.assertFalse(board.remove("missing"))
        self.assertEqual(len(board), 99)

    def test_avl_ties(self):
        board = LeaderboardAVL()
        board.update("b", 17.0)
        board.update("a", 17.0)
        self.assertEqual(board.rankings(), [(17.0, "a"), (17.0, "b")])


if __name__ == "__main__":
    unittest.main()
