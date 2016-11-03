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

from .. import excepts
from .. import elements
from .. import page_base
from .. import login_base

from . import admin_home

logger = logging.getLogger(__name__)

# Model for admin
# location = ''.join([config.url, config.webadmin_entry_point])
location = "https://rhevm40.spice.brq.redhat.com/ovirt-engine/webadmin/"

class AdminLoginPage(login_base.LoginPageBase):
    """Login page abstraction class.

    Parameters
    ----------
      * _location - initial URL to load upon instance creation
    """
    _location = location

    def login_user(self, username, password, domain=None):
        """Login user - fill in the credentials and submit form.

        Parameters
        ----------
          * username - username
          * password - password
          * domain - auth domain; optional, if None, default is used

        Returns
        -------
            HomePage instance.

        Raises
        ------
            InitPageValidationError - all login failure scenarios failed.
        """
        self.fill_form_values(username=username, password=password,
                              domain=domain)
        try:
            home_page = admin_home.AdminHomePage(self.driver)
        except excepts.InitPageValidationError as ex:
            self._proceed_login_error()
            raise ex
        else:
            return home_page
