#!/usr/bin/env python

import sys
sys.path = ['src'] + sys.path

import unittest

from tests import tests_docsearch

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=3).run(
        tests_docsearch.get_all_tests())
