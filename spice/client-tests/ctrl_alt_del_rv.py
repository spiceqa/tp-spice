#!/usr/bin/python
# -*- coding: utf-8 -*-
""" 
Simple script to select the PrintScreen menu option from the client
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
remote.SendKey_Menu("Ctrl+Alt+Del")

