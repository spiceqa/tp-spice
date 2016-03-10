#!/usr/bin/python

""" 
Simple script to leave fullscreen for remote_viewer via keyboard shortcuts
"""
import sys
import time
sys.path.append('./')
from remote_viewer import RemoteViewer

remote = RemoteViewer(1)
if not(remote.rv_available()):
    print "Remote_Viewer is not available"
    sys.exit(1)
remote.open()
remote.raise_window()
#remote.menu_focus()

print "Testing leave full screen via shortcut"
remote.leave_fullscreen(False)
time.sleep(2)
#Verification that remote_viewer is in fullscreen
if (remote.is_fullscreen()):
    remote.leave_fullscreen(False)
    print "First try unseccessful"
    time.sleep(2)
    if (remote.is_fullscreen()):
        print "Error: still in full screen"
        sys.exit(1)
    else:
        print "Verified UI shows remote viewer is not in full screen mode"
else:
    print "Verified UI shows remote viewer is not in full screen mode"
