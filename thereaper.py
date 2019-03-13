#!/usr/bin/python
"""
Purpose: Log out users who have been idle for extended periods.
Calculation of idle time uses the same logic as the Linux w command.
python-utmp found at: https://github.com/garabik/python-utmp
w found at: https://gitlab.com/procps-ng/procps/blob/
f71405b44d6a1488452fa95f16df021d90e7b489/w.c
"""
import os, signal, stat, time
from utmp import UtmpRecord
from optparse import OptionParser


parser = OptionParser()
parser.add_option('-n', type='int', dest='numberofdays', default=30,
                  help='number of days of idleness allowed [default: 30]')
parser.add_option('-k', action='store_true', dest='killidleusers', default=False,
                  help='log out idle users [default: report only]')
(options, args) = parser.parse_args()

# Set how many days we will allow users to remain logged in.
DAYS_OF_IDLENESS = options.numberofdays
KILL_IDLE_USERS = options.killidleusers

def getidleusers():
    """
    Step through utmp and find interactive user sessions.  Return a list of
    users who have been idle for more than DAYS_OF_IDLENESS days.
    """
    idleusers = []
    for utmpentry in UtmpRecord():
        # utmpentry is a UtmpRecord object
        # Ensure that this utmpentry is a user process.
        if utmpentry[0]==7 and utmpentry[2] != ':0':
            # Use stat to determine the access time for the TTY.  Subtract from the current time,
            # and divide by a day's worth of seconds.
            idle_time = (time.time()-os.stat('/dev/{0}'.format(utmpentry[2])).st_atime)/(3600*24)
            if idle_time > DAYS_OF_IDLENESS:
                idleusers.append([utmpentry[4],utmpentry[2],utmpentry[1],idle_time])
    return idleusers

def printidleusers(idleusers):
    """
    Take two dimensional list of idle users as input, and print the list.
    """
    print 'Users idle for {0} or more days:'.format(DAYS_OF_IDLENESS)
    for idleuser in idleusers:
        print 'user {0}, tty {1}, pid {2}, idle time (days) {3}'.format(idleuser[0],idleuser[1],idleuser[2],idleuser[3])

def killidleusers(idleusers):
    """
    Take two dimensional list of idle users as input, and kill users who have
    been idle for more than DAYS_OF_IDLENESS days.
    """
    for idleuser in idleusers:
        os.kill(idleuser[2], signal.SIGTERM)

idleusers = getidleusers()
printidleusers(idleusers)
# CAUTION!  The following will log out idle users.
if KILL_IDLE_USERS:
    killidleusers(idleusers)
