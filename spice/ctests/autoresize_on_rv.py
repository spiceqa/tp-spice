#!/usr/bin/python

""" 
Simple script to turn on auto resize for the remote viewer window.
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
if remote.is_autoresize():
    pass
else:
    remote.toggle_autoresize()
if not(remote.is_autoresize()):
    sys.exit(1)
print "Auto Resize of Remote Viewer is: " + str(remote.is_autoresize())

