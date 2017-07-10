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

"""Test to verify the license from the About screen of remote-viewer.
"""

import os
import sys
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import rv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

expected = "GNU General Public License"

app = rv.Application(method="mouse")

# Test assumes there is only one virtual display.
assert app.dsp_count() == 1
h_license = app.dsp1.help_license()
logger.info('Got license: %s', h_license)
assert expected in h_license
