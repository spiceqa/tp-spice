#!/usr/bin/python

""" 
Simple script to quit remote_viewer using access keys
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
remote.keyCombo("<Alt>f")
remote.keyCombo("q")
remote.keyCombo("Tab")
remote.keyCombo("Tab")
remote.keyCombo("enter")
