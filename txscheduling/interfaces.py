import zope.interface


class ISchedule(zope.interface.Interface):
    """The ISchedule interface describes the interface from merging the wall
    based clock of the twisted timer with a world time based scheduling system.
    In this regard, there is only a single method, getDelayForNext which
    returns the number of seconds needed to wait until the next execution
    should occur. """
    
    
    def getDelayForNext(self):
        """Return the delay before the next execution in seconds.
        
        @rtype: C{float}
        @return: The number of seconds to delay before the next execution of
        this schedule.
        """