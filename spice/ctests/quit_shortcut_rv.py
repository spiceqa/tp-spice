#!/usr/bin/python

""" 
Simple script to quit remote_viewer
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
remote.quit(False)
#remote.quit(True)
remote.keyCombo('Tab')
remote.keyCombo('Tab')
remote.keyCombo('enter')
