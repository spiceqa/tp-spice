#!/usr/bin/python

""" 
Script to take a screenshot of the guest vm and save the image
as a custom name in the default Pictures location.
"""
import sys
sys.path.append('./')
from remote_viewer import RemoteViewer

cname = "custom_name.tiff"

remote = RemoteViewer(1)
if not(remote.rv_available()):
    print "Remote_Viewer is not available"
    sys.exit(1)
remote.open()
remote.raise_window()
remote.menu_focus()
remote.screenshot(cname)

