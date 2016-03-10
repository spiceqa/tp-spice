#!/usr/bin/python
"""
remote_viewer.py - class to manipulate the remote-viewer application with the GUI by using dogtail.

Requires: dogtail, assumes remote-viewer is already running.

Usage Notes: Prior to running the rv interaction commands run the following calls:

remote = RemoteViewer() - initialize with the display of remote-viewer you want control over.
if not(remote.rv_available()):
    print "Remote_Viewer is not available"
    sys.exit(1)
- verify remote_viewer is available, exit if not
remote.open() - opens or verifies the display is open
remote.raise_window() - grab focus on the remote-viewers drawing area.

"""

from dogtail.tree import *
from dogtail.procedural import *
from time import sleep
import subprocess

class RemoteViewer(Window):

    main = ""

    def __init__(self, display = 1):
        self.display = display
        self.window = ""
        self.widget = ""
        self.about = ""
        output = subprocess.Popen("cat /etc/redhat-release", stdout=subprocess.PIPE, shell=True).communicate()[0]
        #output = subprocess.check_output("cat /etc/redhat-release", shell=True)
        self.isRHEL7 = "release 7." in output
         

    def rv_available(self):
        try:
            RemoteViewer.main = root.application('remote-viewer')
        except SearchError:
            return False
        return True

    def open(self):
        if not self.is_checked():
            RemoteViewer.main.child('View').click()
            sleep(1)
            RemoteViewer.main.child('Displays').click()
            sleep(1)  
            RemoteViewer.main.child('Display %d' % self.display).click()
        self.window = RemoteViewer.main.children[self.display-1]
        return self.is_open()

    def close(self, menu = False):
        if self.is_checked():
            if menu:
                self.window.child('View').click()
                sleep(1)
                self.window.child('Displays').click()  
                self.window.child('Display %d' % self.display).click()
                return
            else:
                self.keyCombo('<Alt>F4')                
        return not(self.rv_available())
#        return self.is_open()

    def is_open(self):
        for display, window in enumerate(RemoteViewer.main.children, start = 1):
            if '(%d)' % self.display in window.name:
                return display
        return False

    def is_checked(self):
        return root.application('remote-viewer').child('Display %d' % self.display).isChecked

    def menu_focus(self):
        sleep(1)
        self.window.child('View').click()
        sleep(1)
        self.window.child('View').click()
        sleep(1)

    def zoom_in(self, menu = True):
        if self.isRHEL7:
            if menu:
                zoomin = self.window.child('Zoom In')
                zoomin.doActionNamed('click')
            else:
                self.keyCombo('<Control>plus')
        else:
            attempt = 1
            failed = 0
            if menu:
                self.window.child('View').click()
                sleep(1)
                while attempt < 5: 
                    self.window.child('Zoom').click()
                    sleep(2)
                    attempt += 1
                    if attempt == 5:
                       failed = 1
                    if self.window.child('Zoom In').showing:
                        attempt = 5
                self.window.child('Zoom In').click()
                return failed
            self.keyCombo('<Control>plus')

    def zoom_out(self, menu = True):
        if self.isRHEL7:
            if menu:
                zoomin = self.window.child('Zoom Out')
                zoomin.doActionNamed('click')
            else:
                self.keyCombo('<Control>minus')
        else:
            attempt = 1
            failed = 0
            if menu:
                self.window.child('View').click()
                sleep(1)
                while attempt <5:
                    self.window.child('Zoom').click()
                    sleep(2)
                    attempt += 1
                    if attempt == 5:
                        failed =1
                    if self.window.child('Zoom Out').showing:
                        attempt = 5
                self.window.child('Zoom Out').click()
                return failed
            self.keyCombo('<Control>minus')

    def zoom_norm(self, menu = True):
        if self.isRHEL7:
            if menu:
                zoomin = self.window.child('Normal Size')
                zoomin.doActionNamed('click')
            else:
                self.keyCombo("<Control>0")
        else:
            attempt = 1
            failed = 0
            if menu:
                self.window.child('View').click()
                sleep(1)
                while attempt <5:
                    self.window.child('Zoom').click()
                    sleep(2)
                    attempt += 1
                    if attempt == 5:
                        failed =1
                    if self.window.child('Normal Size').showing:
                       attempt = 5

                self.window.child('Normal Size').click()
                return failed
            #I believe the commented out keycombo should work
            #not sure if the way it does work is just a workaround.
            #self.keyCombo("<Control>0")
            self.keyCombo("<Control>_0")


    def fullscreen_toggle(self, menu = False):
        if menu:
            self.window.child('View').click()
            sleep(1)
            self.window.child('Full screen').click()
            sleep(1)
            return
        self.keyCombo('F11')

    def is_fullscreen(self):
        return root.application('remote-viewer').child('Full screen').isChecked

    def leave_fullscreen(self, menu = False):
        if self.isRHEL7:
            if menu:
                leavefullscreen = self.window.child('Leave fullscreen')
                leavefullscreen.doActionNamed('click')
            else:
                sleep(3)
                xcord = self.window.size[0]/2
                print xcord
                rawinput.absoluteMotion(xcord, 0)
                keyCombo('F11')
                #rawinput.pressKey('F11')
        else:
            #first only brings focus to the panel that contains the Leave fullscreenoption
            self.window.children[0].children[1].children[0].click()
            #self.window.child('Leave fullscreen').click()
            sleep(2)
            #Now the operation to leave fullscreen will be performed
            if menu:
                if self.window.child('Leave fullscreen').showing:
                    self.window.child('Leave fullscreen').click()
                    return
                else:
                    #calling the leave full screen twice
                    print "Not showing"
                    self.window.child('Leave fullscreen').click()
                    self.window.child('Leave fullscreen').click()
                    return
            keyCombo('F11')
        
    def is_autoresize(self):
        return self.window.child('Automatically resize').isChecked

    def toggle_autoresize(self):
        self.window.child('View').click()
        sleep(1)
        self.window.child('Automatically resize').click()

    def get_widget(self):
        return self.window.children[0].children[1].children[1].children[1].children[0].children[0]

    def raise_window(self):
        self.get_widget().grabFocus()

    def keyCombo(self, combo, widget = False):
        if widget:
            return self.get_widget().keyCombo(combo)        
        return self.window.keyCombo(combo)
        
    def typeText(self, text, widget = False):
        if widget:
           return self.get_widget().typeText(text)
        return self.window.typeText(text)

    def SendKey_Menu(self, key):
        """
        Valid values for key are:
        Ctrl+Alt+Del, Ctrl+Alt+Backspace
        Ctrl+Alt+F1, Ctrl+Alt+F2, Ctrl+Alt+F3, Ctrl+Alt+F4
        Ctrl+Alt+F5, Ctrl+Alt+F6, Ctrl+Alt+F7, Ctrl+Alt+F8
        Ctrl+Alt+F9, Ctrl+Alt+F10, Ctrl+Alt+F11, Ctrl+Alt+F12
        PrintScreen
        """
        self.window.child('Send key').click()
        sleep(1)
        
        try:
            self.window.child(key).click()
        except SearchError:
            return False
        return True
        

    def help(self, menu = True):
        if menu:
            self.window.child('Help').click()
            sleep(1)
            self.window.child('About').click()

            #Verify there is a Credits, License, and Close button
            try:
                #self.about = RemoteViewer.main.children[-1]
                self.about = RemoteViewer.main.child("About Virtual Machine Viewer",roleName = "dialog")
                verifylist = []
                verifylist.append(self.about.childNamed('Credits').roleName == "push button")
                verifylist.append(self.about.childNamed('License').roleName == "push button")
                verifylist.append(self.about.childNamed('Close').roleName == "push button")
                #verify Credits, License, and Close are all push buttons:
                if all(bool for bool in verifylist):
                    return self.about.children[0].children[0].children[1].text
                else:
                    return "None"
            except SearchError:
                return "None"
        return "None"
    
    def help_license(self, menu = True):
        self.help()
        self.about.child('License').click()
        license = RemoteViewer.main.child("License",roleName = "dialog")
        #print license.text#license.dump()
        return license.children[0].children[0].children[0].text
 
    def help_credits(self, menu = True):
        credits_info_list = [] 
        self.help()
        self.about.child('Credits').click()
        credits = RemoteViewer.main.child("Credits",roleName = "dialog")
        credits.child("Written by").click()
        credits_info_list.append(credits.child("Written by").children[0].children[0].text)
        credits.child("Translated by").click()
        credits_info_list.append(credits.child("Translated by").children[0].children[0].text)
          
        return credits_info_list
   
    def closeabout(self, menu = True):
        self.about = RemoteViewer.main.child("About Virtual Machine Viewer",roleName = "dialog")
        #Close any subdialogs if they exist (License or Credits)
        try:
            license = RemoteViewer.main.child("License",roleName = "dialog")
            license.child('Close').click()
        except SearchError:
            pass
        try:
            credits = RemoteViewer.main.child("Credits",roleName = "dialog")
            credits.child('Close').click()
        except SearchError:
            pass
        self.about.child('Close').click()
        #RemoteViewer.main.children[-1].childNamed('Close').click()

    def quit(self, menu = False):
        if menu:
            self.window.child('File').click()
            sleep(1)
            self.window.child('Quit').click()
            return
        self.keyCombo('<Control><Shift>Q')

    def screenshot(self, name = None):
        self.window.child('File').click()
        self.window.child('Screenshot').click()
        if name:
            root.application('remote-viewer').children[-1].childLabelled('Name:').text = name
        root.application('remote-viewer').children[-1].child('Save').click()

    def connect(self, url):
        #This must be called prior to calling open, since there are no display windows.
        Dialog = RemoteViewer.main.child('Connection details')
        URLTextField = Dialog.children[0].children[0].children[0]
        URLTextField.grabFocus()
        sleep(1)
        URLTextField.typeText(url)
        sleep(1)
        Dialog.child('Connect').click()
        
