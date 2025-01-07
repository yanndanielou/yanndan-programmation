# -*-coding:Utf-8 -*
""" test custom """
import unittest

import unit_tests_helpers
from  custom_iterator import SimpleIntCustomIncrementDecrement

class SimpleIntCustomIncrementDecrementTest(unit_tests_helpers.TestCaseBase):
    """ SimpleIntCustomIncrementDecrementTest """

    def test_increment(self):
        """ test """
        increment_test:SimpleIntCustomIncrementDecrement = SimpleIntCustomIncrementDecrement()
        self.assertEqual(0, increment_test.value)
        self.assertEqual(1, increment_test.prefix_increment())
        self.assertEqual(1, increment_test.value)
        self.assertEqual(2, increment_test.prefix_increment())
        self.assertEqual(2, increment_test.value)
        self.assertEqual(2, increment_test.postfix_increment())
        self.assertEqual(3, increment_test.value)

    def test_decrement(self):
        """ test """
        increment_test:SimpleIntCustomIncrementDecrement = SimpleIntCustomIncrementDecrement(10)
        self.assertEqual(10, increment_test.value)
        self.assertEqual(9, increment_test.prefix_decrement())
        self.assertEqual(9, increment_test.value)
        self.assertEqual(8, increment_test.prefix_decrement())
        self.assertEqual(8, increment_test.value)
        self.assertEqual(8, increment_test.postfix_decrement())
        self.assertEqual(7, increment_test.value)


if __name__ == "__main__":
    unittest.main()
