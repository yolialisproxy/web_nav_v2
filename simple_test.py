
import sys
sys.path.insert(0, 'tests')

from test_e2e import TestE2E
from playwright.sync_api import sync_playwright
import unittest

class SimpleTest(TestE2E):
    def test_simple_load(self):
        self._load()
        print("Page loaded successfully")
        # Just check for any errors
        if self.errors:
            print(f"Errors found: {self.errors}")
        else:
            print("No errors found")
        return len(self.errors) == 0

if __name__ == "__main__":
    # This is a bit hacky but let's try to run just our test
    suite = unittest.TestSuite()
    suite.addTest(SimpleTest('test_simple_load'))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
