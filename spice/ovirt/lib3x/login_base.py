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

import page_base
import elements


logger = logging.getLogger(__name__)


class LoginPageBaseModel(page_base.PageModel):
    """Common page model for the login page.
    """
    username = elements.TextInput(by=by.By.ID, locator='LoginFormView_userName')
    password = elements.PasswordInput(by=by.By.ID,
                                     locator='LoginFormView_password')
    domain = elements.Select(by=by.By.ID, locator='LoginFormView_profile')
    autoconnect = elements.Checkbox(
        by=by.By.ID, locator='LoginFormView_connectAutomaticallyEditor')
    login_btn = elements.Button(by=by.By.ID,
                               locator='LoginFormView_loginButton')
    page_body = elements.PageElement(by.By.TAG_NAME, 'body')
    msg_login_failed = 'The user name or password is incorrect.'
    msg_empty_field = "This field can't be empty."


class LoginPageBase(page_base.PageObject):
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
    _model = LoginPageBaseModel
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
