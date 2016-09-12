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

from selenium.webdriver.common import by
from selenium import common

import page
import element
import exceptions
import homepage

# Model for admin
location = ''.join([config.url, config.webadmin_entry_point])

class AdminLoginPage(LoginPageBase):
    """Login page abstraction class.

    Parameters
    ----------
      * _location - initial URL to load upon instance creation
    """
    _location = m_loginpage.location

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
            home_page = homepage.HomePage(self.driver)
        except exceptions.InitPageValidationError as ex:
            self._proceed_login_error()
            raise ex
        else:
            return home_page

class LoginPageBase(page.PageObject):
    """Common class for admin/user pages. Base page object for login page.

    Parameters
    ----------
    _location
        Initial URL to load upon instance creation.
    _model
        Page model.
    """
    __metaclass__ = abc.ABCMeta
    _location = None
    _model = m_loginpage.LoginPage
    _label = 'login page'

    def init_validation(self):
        """Initial validation - check that login form is loaded.

        Returns
        -------
        bool
            True - successful validation.
        """
        self._model.username
        self._model.password
        self._model.domain
        self._model.login_btn
        return True

    def fill_form_values(self, username, password, domain=None,
                         autoconnect=None):
        """Fill in the login form and submit.

        Parameters
        ----------
        username
            Username.
        password
            Password.
        domain
            Auth domain; optional, if None, default is used.
        autoconnect
            Auto connect to VM console; optional, UP only.

        Returns
        -------
        bool
            True - success.
        """
        self._model.username = username
        self._model.password = password
        self._model.domain = domain
        self._model.autoconnect = autoconnect
        self._model.login_btn.click()
        return True

    @abc.abstractmethod
    def login_user(self):
        """Abstract method.  Login user - fill in the login form and wait for
        home page.
        """
        raise NotImplementedError("abstract method")

    def _proceed_login_error(self):
        """ Proceed login error process. Check particular fail scenarios and
        raise appropriate exception, otherwise return None.

        Returns
        -------
        None

        Raises
        ------
        FieldIsRequiredError
            Username/password is missing.
        LoginError
            Invalid username/password.
        """
        try:
            if self._model.msg_login_failed in self._model.page_body.text:
                raise exceptions.LoginError()
        except common.exceptions.NoSuchElementException:
            pass
        try:
            if (self._model.username.get_attribute('title')
                    == self._model.msg_empty_field):
                raise exceptions.FieldIsRequiredError("username")
        except common.exceptions.NoSuchElementException:
            pass
        try:
            if (self._model.password.get_attribute('title')
                    == self._model.msg_empty_field):
                raise exceptions.FieldIsRequiredError("password")
        except common.exceptions.NoSuchElementException:
            pass

# Common page model

class LoginPage(page.PageModel):
    """Common page model for the login page.
    """
    username = element.TextInput(by=by.By.ID, locator='LoginFormView_userName')
    password = element.PasswordInput(by=by.By.ID,
                                     locator='LoginFormView_password')
    domain = element.Select(by=by.By.ID, locator='LoginFormView_profile')
    autoconnect = element.Checkbox(
        by=by.By.ID, locator='LoginFormView_connectAutomaticallyEditor')
    login_btn = element.Button(by=by.By.ID,
                               locator='LoginFormView_loginButton')
    page_body = element.PageElement(by.By.TAG_NAME, 'body')
    msg_login_failed = 'The user name or password is incorrect.'
    msg_empty_field = "This field can't be empty."
