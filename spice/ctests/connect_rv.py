#!/usr/bin/python

""" 
Simple script to connect to remote_viewer
"""
import os, sys, time
from dogtail.tree import *
from dogtail.procedural import *

#Get the url to connect to from command line input
if len(sys.argv) < 2:
    print "A url to connect to was not entered"
    sys.exit(1)


sys.path.append('./')

killrvcmd = "killall remote-viewer"
rval = os.system(killrvcmd)
print "Return Value of " + killrvcmd + ": " + str(rval)
rval = os.system("remote-viewer &")
if rval != 0:
   print "Remote Viewer did not start as expected, Ending Test"
   sys.exit(1)

urltext = sys.argv[1]
ticket = None
if len(sys.argv) == 3:
    ticket = sys.argv[2]

rvbase = root.application('remote-viewer')
ConnectDetailsDialog = rvbase.children[0] #.click()
URLDialog = ConnectDetailsDialog.children[0].children[0].children[0]
URLDialog.click()
URLDialog.typeText(urltext)

ConnectButton = ConnectDetailsDialog.childNamed('Connect')
ConnectButton.click()

time.sleep(5)

if ticket:
    rvbase = root.application('remote-viewer')
    authDialog = rvbase.children[1]
    passwordDialog = authDialog.children[0].children[1].children[1]
    passwordDialog.click()
    passwordDialog.typeText(ticket)
    rvbase.keyCombo('enter')
