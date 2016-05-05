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


"""Close remote_viewer.
"""

import os
import sys
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import rv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

rv_app = rv.Application(method="mouse")
# Test assumes there is only one virtual display.
assert rv_app.dsp_count() == 1
logger.info("Close by deselecting last display.")
rv_app.dsp1.close(1)
assert rv_app.app.dead
