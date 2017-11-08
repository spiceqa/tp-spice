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


"""Failed to connect to remote-viewer. Examining content of alert message.
"""

import os
import sys
import logging

logger = logging.getLogger(__name__)


def run(helper):
    cfg = helper.query_master("get_cfg")
    dbus = helper.query_master("get_x_var", "DBUS_SESSION_BUS_ADDRESS",
                               cfg["client_vm"])
    helper.info("Dbus: %s.", repr(dbus))
    os.environ['DBUS_SESSION_BUS_ADDRESS'] = dbus
    uri = helper.query_master("get_uri")
    helper.info("Uri: %s.", repr(uri))
    os.environ['DISPLAY'] = ":0.0"
    sys.path.append(os.path.dirname(__file__))
    try:
        # Up to this point DBUS_SESSION_BUS_ADDRESS / DISPLAY must be set.
        import rv
    except Exception as e:
        helper.info("Cannot import rv: %s.", repr(e))
        return 1
    try:
        rv_app = rv.Application()
    except Exception as e:
        # No running RV. Pass.
        helper.info("Test failed with: %s.", repr(e))
        return 1
    cdir = os.path.dirname(__file__)
    with open(os.path.join(cdir, '..', cfg["rv_file"]), 'r') as f:
        ver_lines = f.readlines()
        ver_line = [l for l in ver_lines if 'versions' in l][0]
        ver = ver_line.split(':')[-1].strip()
    error_message = cfg["error_msg"] % ver
    if cfg.has_key("new_ver"):
        error_message += ', see %s for details' % cfg["new_ver"]
    try:
        rv_app.app.childNamed(error_message)
    except Exception as e:
        helper.info("Test failed with: %s.", repr(e))
        return 1
    helper.info("Test passed. Alert message: '%s' was found.", error_message)
    return 0
