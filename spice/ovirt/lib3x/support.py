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

from selenium.webdriver.support.ui import WebDriverWait as BaseWebDriverWait

import excepts

logger = logging.getLogger(__name__)

POLL_FREQUENCY = 1


class WebDriverWait(BaseWebDriverWait):
    """Overridden <selenium.webdriver.support.ui.WebDriverWait> class.  The
    only difference is updated POLL_FREQUENCY from 0.5 to 1 second.
    """

    def __init__(self, driver, timeout, poll_frequency=POLL_FREQUENCY,
                 **kwargs):
        super(WebDriverWait, self).__init__(driver, timeout, poll_frequency,
                                            **kwargs)


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
        self.__wait = WebDriverWait(
            driver=self, timeout=timeout,
            ignored_exceptions=self
            .__IGNORED_EXCEPTIONS)

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
        except excepts.TimeoutException as ex:
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
