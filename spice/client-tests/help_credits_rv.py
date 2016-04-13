#!/usr/bin/python
# -*- coding: utf-8 -*-
""" 
Simple script to verify the version from the About screen of remote viewer
"""
import sys
sys.path.append('./')
from remote_viewer import RemoteViewer

expected_dev1 = "Daniel P. Berrange"
expected_dev2 = "Marc-André Lureau"
expected_trans = "The Fedora Translation Team"

remote = RemoteViewer(1)
if not(remote.rv_available()):
    print "Remote_Viewer is not available"
    sys.exit(1)
remote.open()
remote.raise_window()
#remote.menu_focus()
credit_info = remote.help_credits()
print "Credits Info: " + credit_info[0] + ", and " + credit_info[1]

#verify developers
if expected_dev1 in credit_info[0] and expected_dev2 in credit_info[0]:
   print "Expected developers verified in Credits dialog"
else:
   print expected_dev1 + " or " + expected_dev2 + " not found in: " + credit_info[0]
   sys.exit(1)


#verify translation team
if expected_trans in credit_info[1]:
   print "Expected translation team verified in Credits dialog"
else:
   print expected_trans + " not found in: " + credit_info[1]

remote.closeabout()

