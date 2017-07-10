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

"""Support functionality for Selenium WebDriver.
"""

import logging

from selenium import common
from selenium.webdriver.support import ui

from . import excepts

logger = logging.getLogger(__name__)


POLL_FREQUENCY = 1

#WebDriverWait == from selenium.webdriver.support import ui.WebDriverWait
#poll_frequency=POLL_FREQUENCY


class WaitForPageObject(object):
    """Wrapper around WebDriverWait providing helper methods for page objects.

    Example
    -------

        template = TemplateInstance(driver, name='test-tmpl')

        WaitForPageObject(template, 60).to_disappear()
        WaitForPageObject(template, 30).status('is_ok')
        WaitForPageObject(template, 30).status_not('is_locked')
        ...

    """
    __IGNORED_EXCEPTIONS = excepts.InitPageValidationError
    __DISAPPEAR_TIMEOUT = 1

    def __init__(self, page_object, timeout=None):
        timeout = timeout or 0
        self.__page_object = page_object
        self.__wait = ui.WebDriverWait(
            driver=self,
            # astepano@: what the ...?????? It wasn't me who wrote this!
            #  This object is only for methods: until_not/until
            #  .driver will be passed as an argument to until.
            #  See: (/usr/lib/python2.7/site-packages/selenium/webdriver/
            #        support/wait.py)
            #     def until(self, method, message=''):
            #        """Calls the method provided with the driver as
            #        an argument until the return value is not False.
            #        """
            #        ....
            #        value = method(self._driver)
            # F@CK!!!!!!!!
            timeout=timeout,
            poll_frequency=POLL_FREQUENCY,
            ignored_exceptions=self.__IGNORED_EXCEPTIONS)

    @property
    def __validated_page_object(self):
        """Runs init validation before the page object is returned.
        """
        self.__page_object._initial_page_object_validation()
        return self.__page_object

    def to_disappear(self, message=None):
        """Waits until the page object is no longer present on the page.

        Parameters
        ----------
        message : str
            Error message.
        """
        message = message or '%s is still present' % self.__page_object
        original_timeout = self.__page_object._timeout
        self.__page_object.driver.implicitly_wait(self.__DISAPPEAR_TIMEOUT)
        try:
            self.__wait.until_not(lambda self: self.__validated_page_object,
                                  message=message)
        except common.exceptions.TimeoutException as ex:
            self.__page_object.driver.implicitly_wait(original_timeout)
            raise ex

    def status(self, status_prop, message=None):
        """Waits until page object property `status_prop` is evaluated as True.

        Parameters
        ----------
        status_prop : str
            Name of the page object status property; the property should return
            only bool, not string.
        message : str
            Error message.
        """
        message = message or '%s: status is "%s"' % (self.__page_object,
                                                     self.__page_object.status)
        self.__wait.until(lambda self:
                          getattr(self.__page_object, status_prop),
                          message=message)

    def status_not(self, status_prop, message=None):
        """Waits until page object property `status_prop` is evaluated as
        False.

        Parameters
        ----------
        status_prop : str
            Name of the page object status property; the property should return
            only bool, not string.
        message : str
            Error message.
        """
        message = message or '%s: status is "%s"' % (self.__page_object,
                                                     self.__page_object.status)
        self.__wait.until_not(lambda self:
                              getattr(self.__page_object, status_prop),
                              message=message)
