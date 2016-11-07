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

"""Push RV into zoom mode.
"""

import os
import sys
import logging
from distutils import util
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import rv
import argparse
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description='Push RV zoom mode.')
group = parser.add_mutually_exclusive_group(required=True)
parser.add_argument("direction", help="Zoom direction.",
                    choices=['in', 'out', 'normal'] )
group.add_argument("-a", "--accesskeys", help="Use access keys.",
                   action="store_const", const="access_key", dest="method")
group.add_argument("-k", "--hotkeys", help="Use hot keys.",
                   action="store_const", const="hot_key", dest="method")
group.add_argument("-m", "--mouse", help="Use mouse.", action="store_const",
                   const="mouse", dest="method")
group.add_argument("-w", "--windowmanager", help="Use window manager.",
                   action="store_const", const="wm_key", dest="method")
parser.add_argument("-r", "--repeat", help="Repeat zooming.", default=0, 
                   dest="repeat", type=int)
parser.add_argument("-R", "--reset", help="Reset to normal size afterwards.", action="store_true")
args = parser.parse_args()

app = rv.Application(method=args.method)
# Test assumes there is only one virtual display.
assert app.dsp_count() == 1
app.dsp1.key_combo('<Super_L>Down')
time.sleep(1)
logger.info("Dislay #%s extents before %s zoom: %s", app.dsp1.num,
            args.direction, app.dsp1.dsp.extents)
_, _, w1, h1 = app.dsp1.dsp.extents
for i in range(args.repeat + 1):
    app.dsp1.zoom(args.direction)
    _, _, w2, h2 = app.dsp1.dsp.extents
    logger.info("Dislay #%s extents after %s zoom: %s", app.dsp1.num, args.direction, app.dsp1.dsp.extents)
    if args.direction == "in":
        assert w2 >= w1
        assert h2 >= h1
    elif args.direction == "out":
        assert w2 <= w1
        assert h2 <= h1
if args.direction == "normal" or args.reset:
    if args.reset:
        app.dsp1.zoom()
    _, _, w2, h2 = app.dsp1.dsp.extents
    logger.info("Dislay #%s extents after %s zoom: %s", app.dsp1.num, args.direction, app.dsp1.dsp.extents)
    assert w2 == w1
    assert h2 == h1

