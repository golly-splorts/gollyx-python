import unittest
from .fixtures import (
    two_spinners_fixture,
    two_acorn_fixture,
    multicolor_crux_fixture,
    multicolor_pi_fixture,
    bigass_random_fixture,
)


class FixturesTest(unittest.TestCase):
    def test_two_spinner_fixture(self):

        binary, s1, s2 = two_spinners_fixture()

        self.assertTrue(binary.contains(1, 1))
        self.assertTrue(binary.contains(1, 2))
        self.assertTrue(binary.contains(1, 3))

        self.assertTrue(binary.contains(10, 15))
        self.assertTrue(binary.contains(10, 16))
        self.assertTrue(binary.contains(10, 17))

        self.assertTrue(s1.contains(1, 1))
        self.assertTrue(s2.contains(1, 2))
        self.assertTrue(s1.contains(1, 3))

        self.assertTrue(s2.contains(10, 15))
        self.assertTrue(s1.contains(10, 16))
        self.assertTrue(s2.contains(10, 17))

    def test_two_acorn_fixture(self):

        binary, s1, s2 = two_acorn_fixture()

    def test_multicolor_crux_fixture(self):

        binary, s1, s2 = multicolor_crux_fixture()

    def test_multicolor_pi_fixture(self):

        binary, s1, s2 = multicolor_pi_fixture()

    def test_bigass_random_fixture(self):

        binary, s1, s2 = bigass_random_fixture()
