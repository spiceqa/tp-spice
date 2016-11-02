#!/usr/bin/python

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.

"""Manipulate remote-viewer GUI by using dogtail.

Requires
--------
    dogtail.
    running remote-viewer.

Notes
-----
    Prior to running the rv interaction commands run the following calls:

        remote = RemoteViewer()

    initializes with the display of remote-viewer you want control over.
    remote.open() - opens or verifies the display is open
    remote.raise_window() - grab focus on the remote-viewers drawing area.

"""

import os
import sys
import logging
from dogtail import utils
utils.enableA11y()
from dogtail import tree
from dogtail import predicate
import platform
import time
import commands

sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import retries

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class GeneralError(Exception):
    pass


def is_rhel7():
    return '7.' in platform.dist()[1]


def do_click(node):
    is_showing(node)
    if node.roleName == 'menu' \
            or node.roleName == 'radio button':
        click_and_focused(node)
    if node.roleName == 'menu item' \
            or node.roleName == 'check menu item':
        point_and_focused(node)
        node.click()
    if node.roleName == 'push button':
        point_and_pointed(node)
        node.click()


#dump(tree.root.application('remote-viewer'))
def dump(node):
    for i in node.children:
        logger.info("%s %s %s", i.focused, i.name, i.roleName)
        dump(i)


def _is_focused(n):
    if n.focused:
        return True
    p = n.parent
    if not p:
        return False
    logger.info("Check if parent [%s | %s] is focused.", p.roleName, p.name)
    return _is_focused(p)

@retries.retries(5, exceptions=(AssertionError,))
def is_focused(node):
    assert _is_focused(node), \
        "Node [%s | %s] is: not focused." % (node.roleName, node.name)
    logger.info("Node [%s | %s] is: focused.", node.roleName, node.name)


@retries.retries(5, exceptions=(AssertionError,))
def is_showing(node):
    assert node.showing, \
        "Node [%s | %s] is: not showing." % (node.roleName, node.name)
    logger.info("Node [%s | %s] is: showing.", node.roleName, node.name)


@retries.retries(5, exceptions=(AssertionError,))
def click_and_focused(node):
    node.click()
    assert _is_focused(node), \
        "Click for node [%s | %s]: failed." % (node.roleName, node.name)
    logger.info("Click for node [%s | %s]: success.", node.roleName, node.name)

@retries.retries(5, exceptions=(AssertionError,))
def point_and_focused(node):
    node.point()
    assert node.focused, \
        "Focus for node [%s | %s]: failed." % (node.roleName, node.name)
    logger.info("Focus for node [%s | %s]: success.", node.roleName, node.name)


@retries.retries(5, exceptions=(AssertionError,))
def point_and_pointed(node):
    node.point()
    assert node.position[0] >= 0
    assert node.position[1] >= 0
    pointX = node.position[0] + node.size[0] / 2
    pointY = node.position[1] + node.size[1] / 2
    assert node.parent.getChildAtPoint(pointX, pointY) == node, \
        "Point for node [%s | %s]: failed." % (node.roleName, node.name)
    logger.info("Point for node [%s | %s]: success.", node.roleName, node.name)


class Display(object):

    def __init__(self, application, num):
        self.application = application  # Application object
        self.app = application.app      # Dogtail object
        self.num = num
        self.dsp = Display.get(self.app, num)  # Dogtail object
        role = 'unknown'
        if self.dsp.isChild(roleName='drawing area'):
            role = 'drawing area'
        self.drawing_area = self.dsp.child(roleName=role)

    @staticmethod
    def get(app, num):
        label_name = 'Waiting for display %s...' % num
        retry = True
        if str(num) == str(1):
            # Do not retry search in case Display#1 is requrested. As it be done
            # further.
            retry = False
        try:
            node = app.child(roleName='label', name=label_name, retry=retry)
        except tree.SearchError:
            # Fail back to case where spice-vdagent is absent, and exists only one
            # display.
            if str(num) != str(1):
                raise GeneralError('Cannot find display %s.' % num)
            role = 'unknown'
            if app.isChild(roleName='drawing area'):
                role = 'drawing area'
            node = app.child(roleName=role)
        pred = predicate.IsAWindow()
        dsp = node.findAncestor(pred)
        return dsp

    @staticmethod
    def make(application, num, method):
        for cls in Display.__subclasses__():
            if cls.is_for(method):
                return cls(application, num)
        raise ValueError



    def typeText(self, text):
        logger.info("Display #%s, type text: %s", self.num, text)
        return self.dsp.window.typeText(text)


    def key_combo(self, combo):
        self.push_front()
        if self.is_fullscreen():
            # remote-viewer intercepts _all_ keys. It is necessary to point to
            # some RV widget.
            n = self.dsp.button('Leave fullscreen')
            point_and_pointed(n)
            # rawinput.absoluteMotion(xcord, 0)
        else:
            point_and_pointed(self.dsp.menu('File'))
        logger.info("Display #%s, send key combo: %s", self.num, combo)
        self.drawing_area.keyCombo(combo)


    def push_front(self):
        self.drawing_area.grabFocus()
        is_focused(self.drawing_area)
        # time.sleep(1) -- It is wrong way to do. Do it in correct way:
        cmd = "xdotool getactivewindow getwindowpid"
        pid_req = self.dsp.get_process_id()
        for i in range(10):
            status, pid = commands.getstatusoutput(cmd)
            pid = int(pid.rstrip('\n'))
            if pid_req == pid:
                break
            logger.info("Active PID: %s, required PID: %s. Waiting #%s.", pid,
                        pid_req, i)
            time.sleep(i)
        assert pid_req == pid


    def is_fullscreen(self):
        flag = self.dsp.menu('View').menuItem('Full screen').isChecked
        if flag:
            virt_dsp_pos = self.dsp.position
            # .. todo:: compare with actual client's resolution.
            if virt_dsp_pos != (0, 0):
                err_msg = "Wrong position %s." % str(virt_dsp_pos)
                raise GeneralError(err_msg)
        return flag


    def is_window(self):
        return not self.is_fullscreen()


    def fullscreen_on(self):
        raise NotImplementedError()


    def fullscreen_off(self):
        raise NotImplementedError()


    def zoom(self, direction):
        raise NotImplementedError()


    def vm_sendkey(self, key):
        raise NotImplementedError()


    def screenshot(self, save_as):
        raise NotImplementedError()


    def closeabout(self):
        assert self.is_window()
        about = self.app.child("About Virtual Machine Viewer", roleName = "dialog")
        about.keyCombo('Esc')

    def confirm_quit(self):
        if self.app.isChild(roleName='alert', name='Question'):
            n = self.app.child(roleName='alert', name='Question').button('OK')
            do_click(n)


class DisplayMouse(Display):

    @classmethod
    def is_for(cls, method):
        return method == 'mouse'

    def app_quit(self):
        logger.info("Close app by accessing Quit menu entry.")
        self.push_front()
        if self.is_window():
            n = self.dsp.menu('File')
            do_click(n)
            n = self.dsp.menu('File').menuItem('Quit')
            do_click(n)
        elif self.is_fullscreen():
            # Button doesn't have a name. See dogtail dump(). Reffer by index.
            panel = self.dsp.button('Leave fullscreen').parent.parent
            n = panel.findChildren(
                # 3 - button #4.
                predicate.GenericPredicate(roleName='push button'))[3]
            do_click(n)
        else:
            raise NotImplementedError()
        assert self.app.dead

    def open(self, num):
        assert self.application.dsp_is_inactive(num)
        self.toggle(num)
        assert self.application.dsp_is_active(num)

    def close(self, num):
        assert self.application.dsp_is_active(num)
        self.toggle(num)
        if self.app.isChild(roleName='alert', name='Question'):
            n = self.app.child(roleName='alert', name='Question').button('OK')
            do_click(n)
        if self.app.dead:
            # RV auto-closes when last display is closed.
            return
        assert self.application.dsp_is_inactive(num)

    def toggle(self, num):
        assert self.is_window()
        self.push_front()
        n = self.dsp.menu('View')
        do_click(n)
        n = self.dsp.menu('View').menu('Displays')
        point_and_focused(n)
        display = 'Display %d' % num
        n = self.dsp.menu('View').menu('Displays').menuItem(display)
        do_click(n)

    def zoom(self, direction='normal'):
        assert self.is_window()
        self.push_front()
        logger.info("Display #%s do zoom: %s", self.num, direction)
        menu = {'in': 'Zoom In',
                'out': 'Zoom Out',
                'normal': 'Normal Size'}
        menu_item = menu[direction]
        n = self.dsp.menu('View')
        do_click(n)
        n = self.dsp.menu('View').menu('Zoom')
        point_and_focused(n)
        n = self.dsp.menu('View').menu('Zoom').menuItem(menu_item)
        do_click(n)


    def screenshot(self, filename):
        assert self.is_window()
        self.push_front()
        n = self.dsp.menu('File')
        do_click(n)
        n = self.dsp.menu('File').menuItem('Screenshot')
        do_click(n)
        file_chooser = self.app.child(roleName='file chooser')
        file_chooser.childLabelled('Name:').text = filename
        n = file_chooser.button('Save')
        do_click(n)
        if self.app.isChild(roleName='alert', name='Question'):
            n = self.app.child(roleName='alert', name='Question').button('Replace')
            do_click(n)


    def fullscreen_on(self):
        assert self.is_window()
        self.push_front()
        n = self.dsp.menu('View')
        do_click(n)
        n = self.dsp.menu('View').menuItem('Full screen')
        do_click(n)
        assert self.is_fullscreen()


    def fullscreen_off(self):
        assert self.is_fullscreen()
        self.push_front()
        n = self.dsp.button('Leave fullscreen')
        do_click(n)
        assert self.is_window()


    def help_license(self):
        # Return license text.
        assert self.is_window()
        self.push_front()
        n = self.dsp.menu('Help')
        do_click(n)
        n = self.dsp.menu('Help').menuItem('About')
        do_click(n)
        about = self.app.child("About Virtual Machine Viewer", roleName = "dialog")
        n = about.child(name="License", roleName="radio button")
        do_click(n)
        licence_txt = about.child(roleName='text')
        return licence_txt.text


    def help_credits(self):
        assert self.is_window()
        self.push_front()
        n = self.dsp.menu('Help')
        do_click(n)
        n = self.dsp.menu('Help').menuItem('About')
        do_click(n)
        about = self.app.child("About Virtual Machine Viewer", roleName = "dialog")
        n = about.child(name="Credits", roleName="radio button")
        do_click(n)
        scroll_panel = about.child(roleName='scroll pane')
        labels = about.findChildren(
            predicate.GenericPredicate(roleName='label'))
        return [i.name for i in labels if i.name]


    def vm_sendkey(self, key):
        logger.info("Send key to guest VM using 'Send key' menu.")
        self.push_front()
        if self.is_window():
            n = self.dsp.menu('Send key')
            do_click(n)
            n = self.dsp.menu('Send key').menuItem(key)
            do_click(n)
        elif self.is_fullscreen():
            # Button doesn't have name. See dogtail dump(). Reffer by index.
            panel = self.dsp.button('Leave fullscreen').parent.parent
            n = panel.findChildren(
                # 1 - button #2.
                predicate.GenericPredicate(roleName='push button'))[1]
            do_click(n)
            # There are two different clones of menu. Operate on second.
            n = self.app.child(roleName='window').child(roleName='menu').menuItem(key)
            do_click(n)
        else:
            raise NotImplementedError()


    def help_version(self):
        logger.info("Get RV version using Help->About dialog.")
        assert self.is_window()
        self.push_front()
        n = self.dsp.menu('Help')
        do_click(n)
        n = self.dsp.menu('Help').menuItem('About')
        do_click(n)
        about = self.app.child("About Virtual Machine Viewer", roleName = "dialog")
        n = about.child(name="About", roleName="radio button")
        do_click(n)
        # Dirty hack, it is because of:
        # [panel | ]
        # [filler | ]
        #   [label | 2.0-7.el7]
        #     [label | A remote desktop client built with GTK-VNC, ...
        #       [filler | ]
        #          [label | virt-manager.org]
        #              [link | ]
        #                  [label | virt-manager.org]
        #                       [link | ]
        #                            [label | virt-manager.org]
        #                                  [link | ]
        #                                        [label | virt-manager.org]
        panel = about.findChildren(
            predicate.GenericPredicate(roleName='panel'))[1]
        filler = panel.children[0]
        # See rv_dogtail.txt
        return filler.children[0].text




class DisplayAccessKey(Display):

    def_key_mapping = {
        'File' : '<Alt>f',
        'File|Quit' : 'q',
        'File|Screenshot' : 's',
        'Help' : '<Alt>h',
        'Help|About' : 'a',
        'View' : '<Alt>v',
        'View|Zoom' : 'z',
        'View|Zoom|Zoom out' : 'o',
        'View|Zoom|Normal size' : 'n',
        'View|Zoom|Zoom in' : 'i',
        'Send key' : '<Alt>s',
        'Send key|Ctrl+Alt+Del' : 'd',
        'Send key|Ctrl+Alt+Backspace' : 'b',
        'Send key|Ctrl+Alt+F1' : '1',
        'Send key|Ctrl+Alt+F2' : '2',
        'Send key|Ctrl+Alt+F3' : '3',
        'Send key|Ctrl+Alt+F4' : '4',
        'Send key|Ctrl+Alt+F5' : '5',
        'Send key|Ctrl+Alt+F6' : '6',
        'Send key|Ctrl+Alt+F7' : '7',
        'Send key|Ctrl+Alt+F8' : '8',
        'Send key|Ctrl+Alt+F9' : '9',
        'Send key|Ctrl+Alt+F10' : '0',
        'Send key|PrintScreen' : 'p',
    }

    @classmethod
    def is_for(cls, method):
        return method == 'access_key'


    def __init__(self, app, num, kmap={}):
        super(DisplayAccessKey, self).__init__(app, num)
        self.kmap = {}
        self.kmap.update(DisplayAccessKey.def_key_mapping)
        self.kmap.update(kmap)


    def menu(self, menu, sub_menu):
        """menu - name for menu. E.g.: File
        sub_menu - [str,...]. Eg.g.: File|Quit
        """
        logger.info("Access a display menu entry using access keys.")
        assert self.is_window()
        self.push_front()
        self.key_combo(self.kmap[menu])
        menu_entry = self.dsp.menu(menu)
        is_focused(menu_entry.children[0])
        for i in sub_menu:
            key = self.kmap[i]
            logger.info("Display #%s, send to menu: %s.", self.num, key)
            menu_entry.keyCombo(key)

    def zoom(self, direction='normal'):
        logger.info("Display #%s do zoom: %s", self.num, direction)
        menus = {'in': 'View|Zoom|Zoom in',
                 'out': 'View|Zoom|Zoom out',
                 'normal': 'View|Zoom|Normal size'}
        self.menu('View', ['View|Zoom', menus[direction]])


    def vm_sendkey(self, key):
        menu = 'Send key|%s' % key
        self.menu('Send key', [menu,])


    def app_quit(self):
        self.menu('File', ['File|Quit'])
        if self.app.isChild(roleName='alert', name='Question'):
            n = self.app.child(roleName='alert', name='Question').button('OK')
            do_click(n)
        assert self.app.dead


    def help_version(self):
        self.menu('Help', ['Help|About'])
        about = self.app.child("About Virtual Machine Viewer", roleName = "dialog")
        # Dirty hack, it is because of:
        # [panel | ]
        # [filler | ]
        #   [label | 2.0-7.el7]
        #     [label | A remote desktop client built with GTK-VNC, ...
        #       [filler | ]
        #          [label | virt-manager.org]
        #              [link | ]
        #                  [label | virt-manager.org]
        #                       [link | ]
        #                            [label | virt-manager.org]
        #                                  [link | ]
        #                                        [label | virt-manager.org]
        panel = about.findChildren(
            predicate.GenericPredicate(roleName='panel'))[1]
        filler = panel.children[0]
        # See rv_dogtail.txt
        return filler.children[0].text


    def screenshot(self, filename):
        self.menu('File', ['File|Screenshot'])
        file_chooser = self.app.child(roleName='file chooser')
        file_chooser.childLabelled('Name:').text = filename
        n = file_chooser.button('Save')
        do_click(n)
        if self.app.isChild(roleName='alert', name='Question'):
            n = self.app.child(roleName='alert', name='Question').button('Replace')
            do_click(n)


class DisplayHotKey(Display):

    # See dogtail/rawinput.py keyNameAliases = {..}
    def_key_mapping = {
        'quit': '<Control><Shift>q',
        'zoom_out': '<Control>minus',
        'zoom_normal': '<Control>0',
        'zoom_in': '<Control><Shift>plus',
        'Ctrl+Alt+Del': '<Control><Alt>End',
    }

    def __init__(self, app, num, kmap={}):
        super(DisplayHotKey, self).__init__(app, num)
        self.kmap = {}
        self.kmap.update(DisplayHotKey.def_key_mapping)
        self.kmap.update(kmap)

    @classmethod
    def is_for(cls, method):
        return method == 'hot_key'

    def zoom(self, direction='normal'):
        kmap_keys =  {'in': 'zoom_in',
                      'out': 'zoom_out',
                      'normal': 'zoom_normal'}
        key = self.kmap[kmap_keys[direction]]
        self.key_combo(key)


    def app_quit(self):
        self.key_combo(self.kmap['quit'])
        if self.app.isChild(roleName='alert', name='Question'):
            n = self.app.child(roleName='alert', name='Question').button('OK')
            do_click(n)
        assert self.app.dead


    def vm_sendkey(self, key):
        self.key_combo(self.kmap[key])


class DisplayWMKey(Display):

    def_key_mapping = {
        'fullscreen': 'F11',
        'quit': '<Alt>F4',
    }

    @classmethod
    def is_for(cls, method):
        return method == 'wm_key'


    def __init__(self, app, num, kmap={}):
        super(DisplayWMKey, self).__init__(app, num)
        self.kmap = {}
        self.kmap.update(DisplayWMKey.def_key_mapping)
        self.kmap.update(kmap)


    def wm_send_key(self, key):
        self.push_front()
        if self.is_fullscreen():
            # remote-viewer intercepts _all_ keys. It is necessary to point to
            # some RV widget.
            n = self.dsp.button('Leave fullscreen')
            point_and_pointed(n)
        else:
            point_and_pointed(self.dsp.menu('File'))
        logger.info("Display #%s, send key: %s", self.num, key)
        time.sleep(1.5)  # Hrrrr!!!!!!!!!!!
        tree.root.keyCombo(key)
        #rawinput.pressKey('F11')


    def app_quit(self):
        assert not self.app.dead
        key = self.kmap['quit']
        self.wm_send_key(key)
        self.confirm_quit()
        assert self.app.dead


    def fullscreen_toggle(self):
        key = self.kmap['fullscreen']
        self.wm_send_key(key)


    def fullscreen_on(self):
        assert self.is_window()
        self.fullscreen_toggle()
        assert self.is_fullscreen()


    def fullscreen_off(self):
        assert self.is_fullscreen()
        # It seems that F11 is processed by WindowManager, not RemoteViewer.
        # It is necessary to point on some RV widget.
        self.fullscreen_toggle()
        assert self.is_window()


# Connect dialog
class Connect(object):

    def __init__(self, application):
        self.application = application  # Application object
        self.app = application.app      # Dogtail object
        self.conn = self.get(self.app)

    @staticmethod
    def get(app):
        assert not app.dead
        scroll_pane = app.child(roleName='scroll pane')
        scroll_pane.grabFocus()
        is_focused(scroll_pane)
        pred = predicate.IsADialogNamed(dialogName='Connection details')
        win = scroll_pane.findAncestor(pred)
        return win

    @staticmethod
    def make(app, method):
        for cls in Connect.__subclasses__():
            if cls.is_for(method):
                return cls(app)
        raise ValueError


class ConnectMouse(Connect):

    @classmethod
    def is_for(cls, method):
        return method == 'mouse'


    def connect(self, url, ticket=""):
        con_addr = self.conn.child(roleName='text')
        con_addr.grabFocus()
        is_focused(con_addr)
        con_addr.typeText(url)
        n = self.conn.child(roleName='push button', name='Connect')
        do_click(n)
        if ticket:
            dialog = self.app.child(name='Authentication required',
                                roleName='dialog')
            passw = dialog.child(roleName='password text')
            passw.typeText(ticket)
            passw.keyCombo('enter')
        # Checks
        assert not self.app.isChild(name='Authentication required',
                                    roleName='dialog', retry=False), \
            "RV asks for ticket."
        assert not self.app.isChild(name='Error', roleName='alert',
                                    retry=False), \
            "RV shows alert pop-up."
        assert not self.app.isChild(name='Connecting to graphic server',
                                    retry=False), \
            "RV stuck at connection to graphic server."
        role = 'unknown'
        if self.app.isChild(roleName='drawing area'):
            role = 'drawing area'
        assert self.app.isChild(roleName=role, retry=False), \
            "No active display."



class Application(object):
    """XXX.

    """
    def __init__(self, app=None, method='mouse'):
        self.app = app
        self.method = method
        if not self.app:
            self.app = self.get()

    @staticmethod
    @retries.retries(2, exceptions=(GeneralError,))
    def get():
        pred = predicate.IsAnApplicationNamed('remote-viewer')
        apps = tree.root.findChildren(pred, recursive=False)
        rv_instances = len(apps)
        try:
            assert rv_instances == 1
        except AssertionError:
            err_msg = "This kind of tests support exactly one instance of RV, " \
                "found %s" % rv_instances
            raise GeneralError(err_msg)
        return apps[0]

    def dsp(self, num):
        return Display.make(self, num=num, method=self.method)

    @property
    def dsp1(self):
        return Display.make(self, num=1, method=self.method)

    @property
    def dsp2(self):
        return Display.make(self, num=2, method=self.method)

    @property
    def dsp3(self):
        return Display.make(self, num=3, method=self.method)

    @property
    def dsp4(self):
        return Display.make(self, num=4, method=self.method)

    @property
    def diag_connect(self):
        return Connect.make(self, method=self.method)

    def dsp_count(self):
        # Get number of active displays.
        role = 'unknown'
        if self.app.isChild(roleName='drawing area'):
            role = 'drawing area'
        pred = predicate.GenericPredicate(roleName=role)
        displays = self.app.findChildren(pred)
        active_displays = len(displays)
        logger.info("remote-viewer has active displays: %s", active_displays)
        return active_displays

    def dsp_is_active(self, num):
        dsp = "Display %s" % num
        return self.app.menu('View').menu('Displays').menuItem(dsp).isChecked

    def dsp_is_inactive(self, num):
        return not self.dsp_is_active(num)
