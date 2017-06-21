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

"""Test fullscreen via the menu options.

    Info
    ----
        Initial condition:

            * remote-viewer is up and running.
            * remote-viwer has one window.
            * remote-viewer is in window mode, not full-screen.
"""


import argparse
import os
import sys
import logging
from distutils import util  # virtualenv problem pylint: disable=E0611
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

import rv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description='Push RV into/from fullscreen mode.')
group = parser.add_mutually_exclusive_group(required=True)
parser.add_argument("fs", help="Fullscreen on/off.",
                    choices=['on', 'off'])
group.add_argument("-a", "--accesskeys", help="Use access keys.",
                   action="store_const", const="access_key", dest="method")
group.add_argument("-k", "--hotkeys", help="Use hot keys.",
                   action="store_const", const="hot_key", dest="method")
group.add_argument("-m", "--mouse", help="Use mouse.", action="store_const",
                   const="mouse", dest="method")
group.add_argument("-w", "--windowmanager", help="Use window manager.",
                   action="store_const", const="wm_key", dest="method")
args = parser.parse_args()


app = rv.Application(method=args.method)

# Test assumes there is only one virtual display.
assert app.dsp_count() == 1

if util.strtobool(args.fs):
    app.dsp1.fullscreen_on()
else:
    app.dsp1.fullscreen_off()
