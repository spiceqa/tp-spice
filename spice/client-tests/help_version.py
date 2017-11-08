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
import argparse
import subprocess

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description='Check remote-viwer version in Help->About.')
group = parser.add_mutually_exclusive_group(required=True)
parser.add_argument("ver", help="Expected version, eg: 2.0-7.el7. If 'find' \
                    specified, currently installed version is automatically \
                    detected.")
group.add_argument("-a", "--accesskeys", help="Use access keys.",
                   action="store_const", const="access_key", dest="method")
group.add_argument("-m", "--mouse", help="Use mouse.", action="store_const",
                   const="mouse", dest="method")
args = parser.parse_args()

app = rv.Application(method=args.method)

# Test assumes there is only one virtual display.
assert app.dsp_count() == 1

version = app.dsp1.help_version()
logger.info('Got version: %s', version)
ver = args.ver
if ver == 'find':
    ver = subprocess.check_output(["rpm", "-q", "virt-viewer", "--queryformat",
                                   "%{VERSION}-%{RELEASE}"])
logger.info('Required version: %s', ver)
assert ver in version
