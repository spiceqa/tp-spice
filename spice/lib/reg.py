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

"""Define zope interfaces that help to indentify a OS. Based on a current
interfaces set we can find most suitable function.

Marker of interface must exactly correspond to a value of an appropritate key
in cartesian config.

Example
-------

    if cartesian_config["os_type"] == "linux":
        print "OS provide ILinux interface."

Example
-------
    In python interpreter:

    # execfile("ios.py")
    # registry.lookupAll([],IOSInfo)
    # registry.lookup([],IVersionMajor,'7')

"""

import logging
from zope import interface
from zope.interface import adapter

logger = logging.getLogger(__name__)

logger.info("Create a new Zope registry.")
registry = adapter.AdapterRegistry()


class IVmAction(interface.Interface):
    def __call__():
        """Run some command on VM."""


def add_action(req, name=None):
    """Register an action for VM, that provides required iface.

    Parameters
    ----------
    req : list
        OS required interfaces.
    name : str, optional.
        Name of provided action. If not specified use a class/function name.

    Returns
    -------
    Interface
        Unmodified function/class.

    """
    def builder(action):
        """
        Parameters
        ----------
        action :
            Something that has __call__()

        """
        action_name = name
        if not action_name:
            action_name = action.__name__
        registry.register(req, IVmAction, action_name, action)
        logger.info("Add VM action: %s for %s.", action_name, repr(req))
        # Next code is not necessary, it stays only for informative purposes.
        provides = list(interface.directlyProvidedBy(action))
        provides.append(IVmAction)
        interface.directlyProvides(action, provides)
        return action
    return builder
