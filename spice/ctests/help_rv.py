#!/usr/bin/python

""" 
Simple script to verify the version from the About screen of remote viewer
"""
import sys
sys.path.append('./')
from remote_viewer import RemoteViewer

#Get the expected version of the cli
if len(sys.argv)!= 2:
    print "Expected version not entered."
    sys.exit(1)

expected_version = sys.argv[1]

remote = RemoteViewer(1)
if not(remote.rv_available()):
    print "Remote_Viewer is not available"
    sys.exit(1)
remote.open()
remote.raise_window()
#remote.menu_focus()
AboutVersion = remote.help()
print AboutVersion
if expected_version in AboutVersion:
   print "Found the expected Verstion:" + expected_version
elif "None" in AboutVersion:
   print "Couldn't get version from About screen"
   sys.exit(1)
else:
   print "The version is incorrect"
   sys.exit(1)
remote.closeabout()

