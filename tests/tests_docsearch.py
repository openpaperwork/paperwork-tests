import unittest

from paperwork.backend import docsearch

class TestDocsearch(unittest.TestCase):
    def setUp(self):
        pass

    def test_init(self):
        pass

    def tearDown(self):
        pass


def get_all_tests():
    all_tests = unittest.TestSuite()

    tests = unittest.TestSuite([
            TestDocsearch("test_init")
        ])
    all_tests.addTest(tests)

    return all_tests
