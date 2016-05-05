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


"""Connect to remote_viewer using 'Connection details' dialog.
"""
import os
import sys
import logging
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import rv
import subprocess
from dogtail import utils

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Connect with remote-viewer.')
parser.add_argument("url", help="Url, eg: spice://127.0.0.1:5960")
parser.add_argument("-t", "--ticket", help="Spice ticket.", default="",
                    nargs="?")
args = parser.parse_args()


assert utils.isA11yEnabled(), "A11 accessibility is disabled."

try:
    rv.Application(method="mouse")
except rv.GeneralError:
    pass
else:
    raise Exception("Found runing RV.")

# Exec new instance RV, without arguments. RV shows 'Connection details.'
# dialog.

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

rv_p = subprocess.Popen(["remote-viewer"])
rv_app = rv.Application(method="mouse")
rv_app.diag_connect.connect(args.url, ticket=args.ticket)
assert rv_app.dsp1
