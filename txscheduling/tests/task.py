import unittest

import zope.interface

from twisted.trial.unittest import TestCase 
from twisted.internet import interfaces, task, reactor, defer, error


from twisted.python import failure

from txscheduling.task import ScheduledCall
from txscheduling.interfaces import ISchedule



class TestableScheduledCall(ScheduledCall):
    """ A ScheduledCall with a different clock """
    def __init__(self, clock, *a, **kw):
        ScheduledCall.__init__(self,*a, **kw)
        self.clock = clock

class SimpleSchedule(object):
    """ A schedule that always returns the same delay for the next call """
    zope.interface.implements(ISchedule)
    
    def __init__(self,delay=1):
        self._delay = delay
    
    def getDelayForNext(self):
        return self._delay

class IncrementingCallable(object):
    def __init__(self):
        self.count = 0
        
    def __call__(self):
        self.count += 1
    

class TestException(Exception):
    pass




class SimpleTests(TestCase):
    """ Tests to verify basic behavior """
    def setUp(self):
        super(SimpleTests, self).setUp()
        self.sc = ScheduledCall(f=lambda: None)
    
    def test_clock(self):
        """ Test that the clock used is the reactor """
        self.assertEqual(self.sc.clock, reactor)
    
    def test_stoppingStopped(self):
        """ Test an invalid stop call to a stopped ScheduledCall """
        self.assertRaises(AssertionError, self.sc.stop)
    
    def test_startingStarted(self):
        """ Test an invalid start call to a running ScheduledCall """
        self.sc.start(SimpleSchedule())
        self.assertRaises(AssertionError,self.sc.start,SimpleSchedule())
        self.sc.stop()
    
    def test_startingInvalidSchedule(self):
        """ Test calling start with an invalid schedule """
        self.assertRaises(TypeError, self.sc.start,'this is garbage')
    
    def test_testStopCallback(self):
        """ Test start deferred callback on stop """
        def cb(result):
            self.assertIdentical(result, self.sc)
        
        d = self.sc.start(SimpleSchedule())
        d.addCallback(cb)
        self.sc.stop()
        
    
class CallableTests(TestCase):
    """ Run tests to verify that the error handling works properly when the 
    callable has problems and that arguments are passed through properly """
    def setUp(self):
        super(CallableTests, self).setUp()
        self.clock = task.Clock()
    
    def test_callable_exception(self):
        """ Test error back call raises exception """
        def f(*args, **kwargs):
            raise TestException('broken')
        
        self.sc = TestableScheduledCall(self.clock, f)
        
        def errback(fail):
            self.assert_(fail.check(TestException),
                         u'Expecting a TestException failure')
        
        def callback(result):
            self.fail('Callback should not be called')
        
        d = self.sc.start(SimpleSchedule(0.1))
        d.addCallbacks(callback, errback)
        self.clock.pump([0.1]*3)
    
    def test_callable_invalid_arguments(self):
        """ Test error back call invalid arguments """
        def f(required, *args, **kwargs):
            raise TestException('broken')
        
        self.sc = TestableScheduledCall(self.clock, f)
        
        def errback(fail):
            self.assert_(fail.check(TypeError),
                         u'Expecting a TypeError failure')
        
        def callback(result):
            self.fail('Callback should not be called')
        
        d = self.sc.start(SimpleSchedule(0.1))
        d.addCallbacks(callback, errback)
        self.clock.pump([0.1]*3)
    
    def test_postional_arguments(self):
        """ Test that positional arguments are passed through properly """
        def f(*args, **kwargs):
            self.assertEqual(len(args),3)
            self.assertEqual(len(kwargs),0)
            self.assertEqual(args[0],'a')
            self.assertEqual(args[1],True)
            self.assertEqual(args[2],'c')
        
        self.sc = TestableScheduledCall(self.clock, f, 'a', True, 'c')
        d = self.sc.start(SimpleSchedule(0.1))
        self.clock.pump([0.1,0.05])
        self.sc.stop()
            
    
    def test_named_arguments(self):
        """ Test that named arguments are passed through properly """
        def f(*args, **kwargs):
            self.assertEqual(len(args),0)
            self.assertEqual(len(kwargs),3)
            self.assertEqual(kwargs['kw1'],'a')
            self.assertEqual(kwargs['kw2'],True)
            self.assertEqual(kwargs['kw3'],'c')
        
        self.sc = TestableScheduledCall(self.clock, f, kw1='a', kw3='c', kw2=True,)
        d = self.sc.start(SimpleSchedule(0.1))
        self.clock.pump([0.1,0.05])
        self.sc.stop()
    
    def test_mixed_arguments(self):
        """ Test that mixed arguments are passed through properly """
        def f(*args, **kwargs):
            self.assertEqual(len(args),2)
            self.assertEqual(len(kwargs),3)
            self.assertEqual(args[0], 'p1')
            self.assertEqual(args[1], False)
            self.assertEqual(kwargs['kw1'],'a')
            self.assertEqual(kwargs['kw2'],True)
            self.assertEqual(kwargs['kw3'],'c')
        
        self.sc = TestableScheduledCall(self.clock, f, 'p1', False, kw1='a',
                                        kw3='c', kw2=True)
        d = self.sc.start(SimpleSchedule(0.1))
        self.clock.pump([0.1,0.05])
        self.sc.stop()


class SimpleTimingTests(TestCase):
    """ Tests to verify simple timing behavior """
    def setUp(self):
        super(SimpleTimingTests, self).setUp()
        self.clock = task.Clock()
        self.callable = IncrementingCallable()
        self.sc = TestableScheduledCall(self.clock, self.callable)
    
    def test_no_calls(self):
        """ No calls before scheduled delay """
        self.sc.start(SimpleSchedule(1))
        self.assertEqual(self.callable.count, 0,
                         u'Callable should not be called before time has passed')
        self.clock.pump([0.9])
        self.assertEqual(self.callable.count, 0,
                         u'Callable should not be called before sufficient time '
                         'has passed')
        self.sc.stop()
        self.assertEqual(self.callable.count, 0,
                         u'Callable should not be called after stopping')
        self.clock.pump([0.1]*50)
        self.assertEqual(self.callable.count, 0,
                         u'Callable should not be called after stopping')
    
    def test_calls(self):
        """ Verify calls at proper times """
        self.sc.start(SimpleSchedule(1))
        self.assertEqual(self.callable.count, 0,
                         u'Callable should not be called before time has passed')
        self.clock.pump([0.1]*11)
        self.assertEqual(self.callable.count, 1,
                         u'Callable should be called once now')
        
        self.clock.pump([0.1]*10)
        self.assertEqual(self.callable.count, 2,
                         u'Callable should be called twice now')
        self.sc.stop()
        self.assertEqual(self.callable.count, 2,
                         u'Callable should not be called after stopping')
        self.clock.pump([0.1]*50)
        self.assertEqual(self.callable.count, 2,
                         u'Callable should not be called after stopping')
        

class LongRunningTimingTests(TestCase):
    def deferredCallable(self, *args, **kwargs):
        self.started()
        return task.deferLater(self.clock, 1.1, self.callable, *args, **kwargs)
    
    def setUp(self):
        super(LongRunningTimingTests, self).setUp()
        self.clock = task.Clock()
        self.callable = IncrementingCallable()
        self.started = IncrementingCallable()
        self.sc = TestableScheduledCall(self.clock, self.deferredCallable)
    
    def test_no_calls(self):
        """ No calls before scheduled delay on long running task """
        self.sc.start(SimpleSchedule(1))
        self.assertEqual(self.callable.count, 0,
                         u'Callable should not be called before time has passed')
        self.assertEqual(self.started.count, 0,
                         u'Callable should not be called before time has passed')
        
        self.clock.pump([0.9])
        self.assertEqual(self.callable.count, 0,
                         u'Callable should not be called before sufficient time '
                         'has passed')
        self.assertEqual(self.started.count, 0,
                         u'Callable should not be called before sufficient time '
                         'has passed')
        self.sc.stop()
        self.assertEqual(self.callable.count, 0,
                         u'Callable should not be called after stopping')
        self.assertEqual(self.started.count, 0,
                         u'Callable should not be called after stopping')
        
        self.clock.pump([0.1]*50)
        self.assertEqual(self.callable.count, 0,
                         u'Callable should not be called after stopping')
        self.assertEqual(self.started.count, 0,
                         u'Callable should not be called after stopping')
        
    
    def test_calls(self):
        """ Verify calls at proper times on long running task """
        self.sc.start(SimpleSchedule(2))
        self.assertEqual(self.callable.count, 0,
                         u'Callable should not be called before time has passed')
        self.assertEqual(self.started.count, 0,
                         u'Callable should not be called before time has passed')
        
        # Time will be approx. 2.1
        self.clock.pump([0.1]*21)
        self.assertEqual(self.callable.count, 0,
                         u'Callable should be running now: %f' % (self.clock.rightNow,))
        self.assertEqual(self.started.count, 1,
                         u'Callable should be running now: %f' % (self.clock.rightNow,))
        
        # Time will be approx. 3.2
        self.clock.pump([0.1]*11)
        self.assertEqual(self.callable.count, 1,
                         u'Callable should be called once now: %f' % (self.clock.rightNow,))
        self.assertEqual(self.started.count, 1,
                         u'Callable should be called once now: %f' % (self.clock.rightNow,))
        
        # Time will be approx. 3.9
        self.clock.pump([0.1]*7)
        self.assertEqual(self.callable.count, 1,
                         u'Callable should be called once now: %f' % (self.clock.rightNow,))
        self.assertEqual(self.started.count, 1,
                         u'Callable should be called once now: %f' % (self.clock.rightNow,))
        
        # Time will be approx 5.2
        self.clock.pump([0.1]*13)
        self.assertEqual(self.callable.count, 1,
                         u'Callable should be running now: %f' % (self.clock.rightNow,))
        self.assertEqual(self.started.count, 2,
                         u'Callable should be running now: %f' % (self.clock.rightNow,))
        
        # Time will be approx. 6.4
        self.clock.pump([0.1]*12)
        self.assertEqual(self.callable.count, 2,
                         u'Callable should be called twice now: %f' % (self.clock.rightNow,))
        self.assertEqual(self.started.count, 2,
                         u'Callable should be called twice now: %f' % (self.clock.rightNow,))
        
        
        self.sc.stop()
        self.assertEqual(self.callable.count, 2,
                         u'Callable should not be called after stopping: %f' % (self.clock.rightNow,))
        self.assertEqual(self.started.count, 2,
                         u'Callable should not be called after stopping: %f' % (self.clock.rightNow,))
        
        
        self.clock.pump([0.1]*50)
        self.assertEqual(self.callable.count, 2,
                         u'Callable should not be called after stopping: %f' % (self.clock.rightNow,))
        self.assertEqual(self.started.count, 2,
                         u'Callable should not be called after stopping: %f' % (self.clock.rightNow,))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(SimpleTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(CallableTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(SimpleTimingTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(LongRunningTimingTests))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())
