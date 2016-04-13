#!/usr/bin/python

""" 
Simple script to verify the license information from the About screen 
of remote viewer using access keys
"""
import sys
sys.path.append('./')
from remote_viewer import RemoteViewer
from dogtail.tree import *

expected_strs_list = []
expected_strs_list.append("This program is free software; you can redistribute it and/or modify")
expected_strs_list.append("it under the terms of the GNU General Public License as published by")
expected_strs_list.append("the Free Software Foundation; either version 2 of the License, or")
expected_strs_list.append("at your option) any later version.")
expected_strs_list.append("This program is distributed in the hope that it will be useful,")
expected_strs_list.append("but WITHOUT ANY WARRANTY; without even the implied warranty of")
expected_strs_list.append("MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the")
expected_strs_list.append("GNU General Public License for more details.")

remote = RemoteViewer(1)
if not(remote.rv_available()):
    print "Remote_Viewer is not available"
    sys.exit(1)
remote.open()
remote.raise_window()
remote.menu_focus()
remote.keyCombo("<Alt>h")
remote.keyCombo("a")
remote.keyCombo("<Alt>l")
rv = root.application('remote-viewer')
license = rv.child("License",roleName = "dialog")
license_info = license.children[0].children[0].children[0].text

print "License Info: " + license_info
for expected_str in expected_strs_list:
   if expected_str in license_info:
       print "found match for str: " + expected_str
   else:
       print "no match found for str: " + expected_str
       print "Actual Text: " + license_info
       sys.exit(1)
remote.closeabout()

