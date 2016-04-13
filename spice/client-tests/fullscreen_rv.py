#!/usr/bin/python

""" 
Simple script to go to fullscreen for remote_viewer via the menu options
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
remote.menu_focus()

#Verification that remote-viewer is not iniatially in fullscreen
if (remote.is_fullscreen()):
    print "Remote Viewer started in full screen, cannot continue the test"
    sys.exit(1)
else:
    pass

#Go to fullscreen via menu
remote.fullscreen_toggle(True)

#Verification that remote_viewer is in fullscreen
if (remote.is_fullscreen()):
    print "Got into full screen"
else:
    print "Test failed"
    sys.exit(1)
