Introduction
============

Twisted provides excellent support for creating delayed calls and looping calls,
but when a daemon runs for extended periods of time, it is often necessary to 
schedule tasks to run in a manner that would be more easily described by a
schedule instead of a number of seconds delay. The twisted.scheduling module 
provides an interface for describing a schedule and a single implementation, a
subset of the cron schedules from linux/Unix. In order to use these schedules,
a ScheduledCall class has been created that acts like the 
twisted.internet.task.LoopingCall class. In the future, an extension of the
twisted.application.internet.TimerService may be provided that would use the
ScheduledCall instead of LoopingCall to provide a similar service.

Cron
====

The cron syntax used follows the crontab syntax listed on the `Wikipedia page 
<http://en.wikipedia.org/wiki/Cron>`_ with the exceptions of the names of the 
days of the week which is not supported and the shortcuts which are also not 
supported.
