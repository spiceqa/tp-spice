#!/usr/bin/python

""" 
Simple script to leave fullscreen for remote_viewer via the menu options
"""
import sys
sys.path.append('./')
from remote_viewer import RemoteViewer

remote = RemoteViewer(1)
if not(remote.rv_available()):
    print "Remote_Viewer is not available"
    sys.exit(1)
remote.open()
remote.raise_window()
#remote.menu_focus()

#Go to fullscreen via menu
#remote.fullscreen_toggle(True)
print "Testing leave full screen"
remote.leave_fullscreen(True)
#Verification that remote_viewer is in fullscreen
if (remote.is_fullscreen()):
    print "Still in full screen"
    sys.exit(1)
else:
    print "No longer in full screen"
