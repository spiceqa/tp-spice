#!/usr/bin/env python
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


"""Classes to work with User/Admin portals loginpages.
"""

import abc
import logging

from selenium.webdriver.common import by
from selenium import common

import elements
import page_base
import login_base
import user_home

logger = logging.getLogger(__name__)

# Model for user
#location = ''.join([config.url, config.user_portal_entry_point])
location = "https://rhevm40.spice.brq.redhat.com/ovirt-engine/userportal/"


class UserLoginPage(login_base.LoginPageBase):
    """Login page abstraction class for IUser portal.

    Parameters
    ----------
    _location
        Initial URL to load upon instance creation.
    """
    _location = location

    def login_user(self, username, password, domain=None, autoconnect=None):
        """Login user - fill in the credentials and submit form.

        Parameters
        ----------
        username
            Username.
        password
            Password.
        domain
            Auth domain; optional, if None, default is used.
        autoconnect
            Auto connect to VM console; optional.

        Returns
        -------
            HomePage instance.

        Raises
        ------
            InitPageValidationError - all login failure scenarios failed
        """
        self.fill_form_values(username=username, password=password,
                              domain=domain, autoconnect=autoconnect)
        try:
            home_page = user_home.UserHomePage(self.driver)
        except excepts.InitPageValidationError as ex:
            self._proceed_login_error()
            raise ex
        else:
            return home_page
