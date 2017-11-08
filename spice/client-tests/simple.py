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


import logging
import os
import commands


def run(helper):
    try:
        cfg = helper.query_master("get_cfg")
        dbus = helper.query_master("get_x_var", "DBUS_SESSION_BUS_ADDRESS",
                                   cfg["client_vm"])
    except Exception as e:
        logging.info("EXC: %s.", str(e))
    logging.info("Dbus: %s.", str(dbus))
    os.environ['DBUS_SESSION_BUS_ADDRESS'] = dbus
    os.environ['DISPLAY'] = ":0.0"
    cdir = os.path.dirname(__file__)
    script = cfg["script"]
    cmd = os.path.join(cdir, script)
    logging.info("Running: %s.", cmd)
    try:
        status, out = commands.getstatusoutput(cmd)
    except Exception as e:
        logging.info("Test failed with: %s.", str(e))
    logging.info("%s finished with: %s", script, out)
    return status
