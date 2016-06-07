#!/usr/bin/env python

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

"""Helper to catch KeyEvents.
"""

import pygtk
pygtk.require('2.0')
import gtk

class TestForm(gtk.Window):

    def __init__(self):
        super(TestForm, self).__init__()

        self.set_title("Key test")
        self.set_size_request(200, 200)
        self.set_position(gtk.WIN_POS_CENTER)

        fixed = gtk.Fixed()

        entry = gtk.Entry()
        fixed.put(entry, 10, 10)

        entry.connect("key_press_event", self.on_key_press_event)

        self.connect("destroy", gtk.main_quit)
        self.add(fixed)
        self.show_all()

        # Clean the text file:
        input_file = open("/tmp/autotest-rv_input", "w")
        input_file.close()

    def on_key_press_event(self, widget, event):
        # Store caught keycodes into text file
        input_file = open("/tmp/autotest-rv_input", "a")
        input_file.write("{0} ".format(event.keyval))
        input_file.close()

if __name__ == "__main__":
    TestForm()
    gtk.main()
