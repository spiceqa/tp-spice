#!/usr/bin/python

from dogtail.tree import *
from time import sleep

class Window(Window):

    def __init__(self, display = 1):
        self.display = display
        self.open()
  
    def open(self):
        if not self.is_checked():
            main = root.application('remote-viewer')
            main.child('View').click()
            sleep(1)
            main.child('Displays').click()
            sleep(1)  
            main.child('Display %d' % self.display).click()
        self.window = root.application('remote-viewer').children[self.display-1]
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
        return self.is_open()

    def is_open(self):
        rv = root.application('remote-viewer')
        for window in rv.children:
            if '(%d)' % self.display in window.name:
                return True
        return False

    def is_checked(self):
        return root.application('remote-viewer').child('Display %d' % self.display).isChecked

    def zoom_in(self, menu = True):
        if menu:
            self.window.child('View').click()
            sleep(1)
            self.window.child('Zoom').click()
            sleep(1)
            self.window.child('Zoom In').click()
            return
        self.keyCombo('<Control>plus')

    def zoom_out(self, menu = True):
        if menu:
            self.window.child('View').click()
            sleep(1)
            self.window.child('Zoom').click()
            sleep(1)
            self.window.child('Zoom Out').click()
            return
        self.keyCombo('<Control>minus')

    def zoom_norm(self, menu = True):
        if menu:
            self.window.child('View').click()
            sleep(1)
            self.window.child('Zoom').click()
            sleep(1)
            self.window.child('Normal Size').click()
            return
        #self.keyCombo('<Control>0')

    def fullscreen_toggle(self, menu = False):
        if menu:
            self.window.child('View').click()
            sleep(1)
            self.window.child('Full screen').click()
            sleep(1)
        self.keyCombo('F11')

    def is_fullscreen(self):
        pass

    def get_widget(self):
        return self.window.children[0].children[1].children[1].children[1].children[0].children[0]

  #  def grab_window(self):
  #      window.

    def keyCombo(self, combo, widget = False):
        if widget:
            return self.get_widget().keyCombo(combo)        
        return self.window.keyCombo(combo)
        
    def typeText(self, text, widget = False):
        if widget:
           return self.get_widget().typeText(text)
        return self.window.typeText(text)

    def help(self):
        pass

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

#root.application('remote-viewer').children[0].children[0].children[1].children[1].children[1].children[0].children[0].grabFocus()
#keyCombo('<Control>F4')
    

