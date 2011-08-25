from datetime import datetime

from unittest import TestCase, TextTestRunner, TestSuite, TestLoader
from doctest import DocTestSuite

from txscheduling import cron
from txscheduling.cron import CronSchedule, InvalidCronLine



class StarTestCase(TestCase):
    def setUp(self):
        self.schedule = CronSchedule('* * * * *')
    
    def testNextMinute(self):
        """ Next runtime is next minute """
        for i in range(0,59):
            self.assertEqual(self.schedule.getNextEntry(datetime(2008, 01, 01,
                                                                 00, i, 00,
                                                                 00)),
                             datetime(2008,01,01,00,i+1,00,00))
    
    def testNextHour(self):
        """ Next runtime is next hour """
        for i in range(0,23):
            self.assertEqual(self.schedule.getNextEntry(datetime(2008, 01, 01, 
                                                                 i, 59, 00,
                                                                 00)),
                             datetime(2008,01,01,i+1,00,00,00))
    
    def testNextDay(self):
        """ Next runtime is next day """
        for i in range(1,31):
            self.assertEqual(self.schedule.getNextEntry(datetime(2008, 01, i, 
                                                                 23, 59, 00, 
                                                                 00)),
                             datetime(2008,01,i+1,00,00,00,00))
    
    def testNextMonth(self):
        """ Next runtime is next month """
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 01, 31, 23,
                                                              59, 00, 00)),
                         datetime(2008,02,01,00,00,00,00))
    
    def testNextYear(self):
        """ Next runtime is next year """
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 12, 31, 23, 
                                                             59, 00, 00)),
                         datetime(2009,01,01,00,00,00,00))

class RangeTestCase(TestCase):
    def setUp(self):
        self.schedule = CronSchedule('15-20 3-6 5-10 5-8 2-3')
    
    def testNextMinute(self):
        """ Test range get next minute """
        # Test minutes that should end up in the current hour at 15 minutes
        for i in range(0,14):
            self.assertEqual(self.schedule.getNextEntry(datetime(2008, 05, 05, 
                                                                 03, i, 00, 
                                                                 00)),
                             datetime(2008,05,05,03,15,00,00))
    
        # Test minutes that should end up in the current hour at i+1 minutes
        for i in range(14,20):
            self.assertEqual(self.schedule.getNextEntry(datetime(2008, 05, 05, 
                                                                 03, i, 00, 
                                                                 00)),
                             datetime(2008,05,05,03,i+1,00,00))
    
        # Test minutes that should end up at hour+1 and 15 minutes
        for i in range(20,60):
            self.assertEqual(self.schedule.getNextEntry(datetime(2008, 05, 05, 
                                                                 03, i, 00, 
                                                                 00)),
                             datetime(2008,05,05,04,15,00,00))
    
    def testNextHour(self):
        """ Test range get next hour """ 
        for i in range(0,3):
            self.assertEqual(self.schedule.getNextEntry(datetime(2008, 05, 05, 
                                                                 i, 59, 00, 
                                                                 00)),
                             datetime(2008,05,05,3,15,00,00))
    
        for i in range(3,6):
            self.assertEqual(self.schedule.getNextEntry(datetime(2008, 05, 05, 
                                                                 i, 59, 00, 
                                                                 00)),
                             datetime(2008,05,05,i+1,15,00,00))
    
        for i in range(6,24):
            self.assertEqual(self.schedule.getNextEntry(datetime(2008, 05, 05, 
                                                                 i, 59, 00, 
                                                                 00)),
                             datetime(2008,05,06,03,15,00,00))
    
    def testNextDay(self):
        """ Test range get next day """
        for i in range(1,5):
            self.assertEqual(self.schedule.getNextEntry(datetime(2008, 05, i, 
                                                                 23, 59, 00, 
                                                                 00)),
                             datetime(2008,05,5,3,15,00,00))
    
        for i in range(5,10):
            self.assertEqual(self.schedule.getNextEntry(datetime(2008, 05, i, 
                                                                 23, 59, 00, 
                                                                 00)),
                             datetime(2008,05,i+1,3,15,00,00))
    
        for i in range(10,13):
            self.assertEqual(self.schedule.getNextEntry(datetime(2008, 05, i, 
                                                                 23, 59, 00, 
                                                                 00)),
                             datetime(2008,05,13,3,15,00,00))
    
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 05, 13, 23, 
                                                             59, 00, 00)),
                         datetime(2008,05,14,3,15,00,00))
    
        for i in range(14,20):
            self.assertEqual(self.schedule.getNextEntry(datetime(2008, 05, i, 
                                                                 23, 59, 00, 
                                                                 00)),
                             datetime(2008,05,20,3,15,00,00))
    
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 05, 20, 23, 
                                                             59, 00, 00)),
                         datetime(2008,05,21,3,15,00,00))
    
    def testNextMonth(self):
        """ Test range get next month """
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 01, 01, 00, 
                                                             00, 00, 00)),
                         datetime(2008,05,05,03,15,00,00))
  
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 05, 31, 23, 
                                                             59, 00, 00)),
                         datetime(2008,06,03,03,15,00,00))
    
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 07, 30, 23, 
                                                             59, 00, 00)),
                         datetime(2008,8,05,03,15,00,00))
    
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 8, 31, 23, 
                                                             59, 00, 00)),
                         datetime(2009,05,05,03,15,00,00))

class AllDOWTestCase(TestCase):
    def setUp(self):
        self.schedule = CronSchedule('*/15 * */5 * *')
  
    def testNextDay(self):
        """ Test all days of the week get next day """
        for i in range(1,30):
            self.assertEqual(self.schedule.getNextEntry(datetime(2008, 01, i, 
                                                                 23, 59, 00, 
                                                                 00)),
                             datetime(2008,01,(i/5)*5+5,00,00,00,00))
  
    def testNextMonth(self):
        """ Test all days of the week get next month """
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 01, 31, 23, 
                                                             59, 00, 00)),
                         datetime(2008,02,05,00,00,00,00))

class FillingCoverageTestCase(TestCase):
    def test_getFirstDayWithSundayDOW(self):
        """ Test next day with Sunday DOW entry """
        schedule = CronSchedule('* * * * 0,3,5')
    
        self.assertEqual(schedule.getNextEntry(datetime(2008,8,31,23,59,00,00)),
                         datetime(2008,9,3,00,00,00,00))

class AllDOMTestCase(TestCase):
    def setUp(self):
        self.schedule = CronSchedule('*/15 * * * 1,3,5')
  
    def testNextDay(self):
        """ Test all days of the month get next day """
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 9, 1, 23, 
                                                             59, 00, 00)),
                         datetime(2008,9,3,00,00,00,00))
    
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 9, 15, 23, 
                                                             59, 00, 00)),
                         datetime(2008,9,17,00,00,00,00))
    
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 9, 16, 23, 
                                                             59, 00, 00)),
                         datetime(2008,9,17,00,00,00,00))
    
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 9, 17, 23, 
                                                             59, 00, 00)),
                         datetime(2008,9,19,00,00,00,00))
  
    def testNextMonth(self):
        """ Test all days of the month get next month """
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 6, 30, 23, 
                                                             59, 00, 00)),
                         datetime(2008,7,2,00,00,00,00))
    
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 8, 29, 23, 
                                                             59, 00, 00)),
                         datetime(2008,9,1,00,00,00,00))
    
        self.assertEqual(self.schedule.getNextEntry(datetime(2008, 9, 29, 23, 
                                                             59, 00, 00)),
                         datetime(2008,10,1,00,00,00,00))

class SimpleTests(TestCase):
    def setUp(self):
        self.schedule = CronSchedule('* * * * *')
    
    def test_invalid_cronline(self):
        """ CronSchedule invalid cron line """
        self.assertRaises(InvalidCronLine,CronSchedule,' ')
    
    def test_equality(self):
        """ CronSchedule equality testing """
        self.assertEqual(self.schedule,CronSchedule('* * * * *'))
        self.assertEqual(self.schedule == 'blah',False)
    
    def test_invalid_call_to_get_next(self):
        """ CronSchedule getNextEntry with invalid arguments """
        self.assertRaises(ValueError,self.schedule.getNextEntry,'')


def test_suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(SimpleTests))
    suite.addTest(TestLoader().loadTestsFromTestCase(AllDOMTestCase))
    suite.addTest(TestLoader().loadTestsFromTestCase(AllDOWTestCase))
    suite.addTest(TestLoader().loadTestsFromTestCase(FillingCoverageTestCase))
    suite.addTest(TestLoader().loadTestsFromTestCase(RangeTestCase))
    suite.addTest(TestLoader().loadTestsFromTestCase(StarTestCase))
    
    suite.addTest(DocTestSuite(cron))
    return suite

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(test_suite())