import unittest

from txscheduling.tests import cron, task

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(cron.test_suite())
    suite.addTests(task.test_suite())
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())
