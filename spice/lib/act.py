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
#
# Copyright: Red Hat Inc. 2016
# Author: Andrei Stepanov <astepano@redhat.com>
#

"""Implements __getattr__ for module.
"""

import sys

class RunAction(object):

    def __getattr__(self, key):
        if key in ["__getstate__", "__setstate__", "__slots__"]:
            raise AttributeError()

        from spice.lib import act2 # There is no namespace for this module.
        return act2.Action(key)

sys.modules[__name__] = RunAction()
