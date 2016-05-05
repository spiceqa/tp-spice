#!/usr/bin/python
# -*- coding: utf-8 -*-

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

"""Verify developers from the About screen of remote viewer.
"""


import os
import sys
import logging
from distutils import util
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import rv
import argparse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = rv.Application(method="mouse")

# Test assumes there is only one virtual display.
assert app.dsp_count() == 1

expected_dev1 = r"Daniel P. Berrange"
expected_dev2 = r"Marc-André Lureau"
expected_trans = r"The Fedora Translation Team"

labels = app.dsp1.help_credits()
logger.info('Got labels: %s', labels)
assert expected_dev1 in labels
assert expected_dev2 in labels
assert expected_trans in labels
app.dsp1.closeabout()
