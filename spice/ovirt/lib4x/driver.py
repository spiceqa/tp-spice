#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylint: disable=R0201,W0235

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


"""Classes difine oVirt pages models.
"""

import os
import time
import types
import logging
import tempfile
import functools

from selenium import webdriver
from selenium import common
from selenium.webdriver.remote import remote_connection
from selenium.webdriver.common import desired_capabilities as dcap


logger = logging.getLogger(__name__)


class FreshWebElement(object):
    """Selenium WebElement proxy/wrapper watching over errors due to element
    staleness.

    Examples
    --------

        console._model.rd_console._elem.is_displayed, is_enabled, ...
        console._model.rd_console._elem.click() == \
            console._model.rd_console.click()

    """

    __ATTEMPTS = 5
    __STALE_ELEM_MSG = "Detected stale element '%s=%s', refreshing (#%s)..."

    def __init__(self, element, by, value):
        """
        Parameters
        ----------
        element : WebElement
            Page element.
        by : str
            Location method.
        value : str
            Locator value.
        """
        self._by = by
        self._value = value
        self._elem = element

    def __refresh_element(self):
        """ Find the element on the page again. """
        driver = self._elem.parent
        self._elem = driver.find_element(by=self._by,
                                         value=self._value,
                                         auto_refresh=False)

    def __getattr__(self, name):
        """Delegates all attribute lookups and method calls to the original
        WebElement and watches for StaleElementReferenceException.  If caught,
        the WebElement is "refreshed", i.e., it's looked up on the page again
        and the attribute lookup or (decorated) method call is executed again
        on the "fresh" element.
        """
        for attempt in range(1, self.__ATTEMPTS + 1):
            try:
                attr = getattr(self._elem, name)
                break
            except common.exceptions.StaleElementReferenceException:
                logger.debug(self.__STALE_ELEM_MSG, self._by,
                             self._value, attempt)
                self.__refresh_element()
        if isinstance(attr, types.MethodType):
            @functools.wraps(attr)
            def safe_elem_method(*args, **kwargs):
                for attempt in range(1, self.__ATTEMPTS + 1):
                    try:
                        attr = getattr(self._elem, name)
                        return attr(*args, **kwargs)
                    except common.exceptions.StaleElementReferenceException:
                        logger.debug(self.__STALE_ELEM_MSG, self._by,
                                     self._value, attempt)
                        self.__refresh_element()
            return safe_elem_method
        return attr


class WebDriverExtension(object):
    """WebDriver extension providing additional functionality. This class
    doesn't have a constructor.
    """

    def _parse_ui_map_locator(self, locator):
        """Parse given ui locator, which must be a 2-item tuple, where first
        item is locator type (see <selenium.webdriver.common.by.By>) and second
        is locator value, e.g., "(By.ID, 'LoginPopupView_userName')".

        Parameters
        ----------
        locator
            2-tuple. 1st item is locator type, 2nd item is value.

        Returns
        -------
        tuple
            2-item tuple.

        Raises
        ------
        ValueError
            Parsing failed.
        """
        try:
            locator_type = locator[0]
            locator_value = locator[1]
        except (IndexError, TypeError):
            raise ValueError("A tuple with two elements is required "
                             "but '%s' given." % locator)
        return (locator_type, locator_value)

    def find_element(self, by, value, auto_refresh=True):
        """Overrides webdriver's method `find_element`.  If `auto_refresh` is
        True, then returns FreshWebElement instance, otherwise the regular
        WebElement.

        Parameters
        ----------
        by : str
            Location method.
        value : str
            Locator value.
        auto_refresh : bool
            True - return FreshWebElement (default), otherwise WebElement
            instance.
        """
        elem = super(WebDriverExtension, self).find_element(by=by, value=value)
        if not auto_refresh:
            return elem
        return FreshWebElement(element=elem, by=by, value=value)

    def find_elements(self, by, value, auto_refresh=True):
        """Overrides webdriver's method `find_elements`.  If `auto_refresh` is
        True, then returns list of FreshWebElement instances, otherwise regular
        list of WebElement instances.

        Parameters
        ----------
        by : str
            Location method.
        value : str
            Locator value.
        auto_refresh : bool
            True - return FreshWebElement (default), otherwise WebElement
            instance.
        """
        elems = super(WebDriverExtension, self).find_elements(by=by,
                                                              value=value)
        if not auto_refresh:
            return elems
        return [FreshWebElement(element=elem, by=by, value=value) for
                elem in elems]

    def find_element_by_ui_map(self, locator):
        """Find element by UI map.

        Parameters
        ----------
        locator
            2-tuple; 1st item is locator type, 2nd item is value.

        Return
        ------
            WebElement instance.
        """
        locator_type, locator_value = self._parse_ui_map_locator(locator)
        return self.find_element(by=locator_type, value=locator_value)

    def find_elements_by_ui_map(self, locator):
        """Find elements by UI map.

        Parameters
        ----------
          locator
            2-tuple; 1st item is locator type, 2nd item is value.

        Returns
        -------
            List of WebElement instance(s).
        """
        locator_type, locator_value = self._parse_ui_map_locator(locator)
        return self.find_elements(by=locator_type, value=locator_value)

    def get_screen_filename(self, prefix=None, suffix=None, use_timestamp=True,
                            dir_=None):
        """Create temporary file and return its filename.

        Parameters
        ----------
        suffix
            File suffix.
        prefix
            File prefix.
        use_timestamp
            True/False; append timestamp to file prefix.
        dir_ : str
            Directory where to store file.

        Returns
        -------
        srt
            Filename, including full path.
        """
        prefix = prefix or 'selenium-screenshot'
        suffix = suffix or '.png'
        dir_ = dir_ or tempfile.gettempdir()
        if use_timestamp:
            timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
            prefix = ''.join((prefix, '-', timestr, suffix))
        abspath = os.path.join(dir_, prefix)
        return abspath

    def save_screen_as_file(self, filename=None):
        """Save the screenshot of the current window.

        Parameters
        ----------
        filename : str
            The full path you wish to save your screenshot to.

        Returns
        -------
        str
            Filename on success.
        """
        filename = filename or self.get_screen_filename()
        if self.get_screenshot_as_file(filename):
            return filename


class Firefox(WebDriverExtension, webdriver.Firefox):
    """Extended Firefox driver.
    """

    def __init__(self, **params):
        super(Firefox, self).__init__(**params)


class Chrome(WebDriverExtension, webdriver.Chrome):
    """Extended Chrome driver.
    """

    def __init__(self, **params):
        super(Chrome, self).__init__(**params)


class Ie(WebDriverExtension, webdriver.Ie):
    """Extended IE driver.
    """

    def __init__(self, **params):
        super(Ie, self).__init__(**params)


class Remote(WebDriverExtension, webdriver.Remote):
    """Extended Remote driver.
    """
    PAGE_LOAD_TIMEOUT = 20

    def __init__(self, **params):
        super(Remote, self).__init__(**params)

    @property
    def __is_ie(self):
        """Returns whether the driver instance is IE or not.
        """
        ie_cap = dcap.DesiredCapabilities.INTERNETEXPLORER
        return self.name in ie_cap['browserName']

    def __ie_confirm_cert_exception(self):
        """Tries to automatically confirm the notorious IE "Certificate Error"
        warning page.  Note that the JS command is called via `get` method,
        because `execute_script` does not work in this case for some reason.
        """
        js_cmd = "javascript:document.getElementById('overridelink').click();"
        try:
            self.set_page_load_timeout(1)
            super(Remote, self).get(js_cmd)
        except common.exceptions.TimeoutException:
            # "Certificate Error" page is not present, moving on
            pass
        finally:
            self.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)

    def get(self, *args, **kwargs):
        """Overridden method. Loads a URL and automatically confirms possible
        HTTPS certificate error warning (for IE only).
        """
        super(Remote, self).get(*args, **kwargs)
        if self.__is_ie:
            self.__ie_confirm_cert_exception()


class SpiceQEFirefoxProfile(webdriver.FirefoxProfile):
    """
    See content type at:

        ~/.mozilla/firefox/<profile_name>/mimeTypes.rdf
        application/x-virt-viewer
    """

    def __init__(self, *args, **kwargs):
        super(SpiceQEFirefoxProfile, self).__init__(*args, **kwargs)
        self.set_preference("browser.download.folderList", 2)
        self.set_preference("browser.download.manager.showWhenStarting", False)
        self.set_preference("browser.download.dir", "~/")
        #self.set_preference("browser.helperApps.neverAsk.saveToDisk",
        #                    "application/x-virt-viewer")
        self.set_preference("browser.helperApps.neverAsk.openFile",
                            "application/x-virt-viewer")


class DriverFactory(object):
    """WebDriver instance factory.

    Attributes
    ----------
    __driver_map_local : dict
        Mapping of local WebDriver classes according to the browser name.
    __desired_capabilities_map : dict
        Mapping of desired capabilities, according to the browser name.
    """
    __driver_map_local = {'Firefox': Firefox,
                          'Chrome': Chrome,
                          'Internet Explorer': Ie}
    __desired_capabilities_map = {'Firefox': dcap.DesiredCapabilities.FIREFOX,
                                  'Chrome': dcap.DesiredCapabilities.CHROME,
                                  'Internet Explorer':
                                  dcap.DesiredCapabilities.INTERNETEXPLORER}

    def __new__(cls, browser_name, host=None, port=None,
                desired_capabilities=None, **kwargs):
        """Return WebDriver instance of desired browser.
        If host and port are specified, remote WebDriver is created,
        otherwise local WebDriver instance is returned.

        Parameters
        ----------
        browser_name : str
            Browser name.
        host : str
            Webdriver server FQDN/IP. Remote driver only.
        port : int
            Webdriver server port. Remote driver only.
        desired_capabilities : dict
            Browser desired capabilities. Use the same format and keys as in
            DesiredCapabilities.*; remote driver only

        Returns
        -------
            Local or remote WebDriver instance.
        """

        if browser_name == 'Firefox':
            logger.info("Add Firefox profile to Selenium webdriver.")
            fp = SpiceQEFirefoxProfile()
            kwargs['browser_profile'] = fp

        if host and port:
            return cls.__get_remote_driver(
                browser_name, host, port, desired_capabilities, **kwargs)
        return cls.__get_local_driver(browser_name, **kwargs)

    @classmethod
    def __get_remote_driver(cls, browser_name, host, port,
                            desired_capabilities=None, **kwargs):
        """Return remote WebDriver instance.

        Returns
        -------
            Remote WebDriver instance.

        Raises
        ------
        KeyError - wrong browser name.
        """
        command_executor = remote_connection.RemoteConnection(
            'http://%s:%s/wd/hub' % (host, port))
        try:
            capabilities = cls.__desired_capabilities_map[browser_name].copy()
        except KeyError:
            raise KeyError("unknown browser: '%s' (valid browsers: %s)" %
                           (browser_name,
                            ', '.join(cls.__desired_capabilities_map.keys())))
        if desired_capabilities:
            capabilities.update(desired_capabilities)

        if browser_name == 'Firefox':
            capabilities['marionette'] = False

        return Remote(command_executor=command_executor,
                      desired_capabilities=capabilities,
                      **kwargs)

    @classmethod
    def __get_local_driver(cls, browser_name, **kwargs):
        """Return local WebDriver instance. For parameters: see `__new__()`.

        Returns
        -------
            Local WebDriver instance.

        Raises
        ------
        KeyError
            Wrong browser name.
        """
        try:
            driver_cls = cls.__driver_map_local[browser_name]
        except KeyError:
            raise KeyError("unknown browser: '%s' (valid browsers: %s)" %
                           (browser_name,
                            ', '.join(cls.__driver_map_local.keys())))
        return driver_cls(**kwargs)

#
# drv = driver.DriverFactory("Firefox", "astepano-ws", "4444")
# capabilities = {
#     'platform': browser_platform,
#     'version': str(browser_version),
# }
# cls.__driver = DriverFactory(browser_name=browser_name, host=host,
#                                 port=port,
#                                 desired_capabilities=capabilities)


# from .ui.common.pages import ApplicationStatus
# from selenium.webdriver.remote import webelement
# from .ui.support import WebDriverWait
# from .ui import exceptions
# from selenium.webdriver.common import action_chains
# def __patch_element_click():
#     """ Now click() method behaves as following:
#      - move the mouse pointer to element and click
#      - if element is not clickable at the moment, throw custom exception
#      - if custom exception is thrown, repeat the click action until timeout
#     """
#     CLICK_TIMEOUT = 5
#
#     def _click_if_clickable(elem):
#         try:
#             ActionChains(elem.parent).click(on_element=elem).perform()
#         except selenium_ex.WebDriverException as ex:
#             if (
#                 ex.msg.startswith('Element is not clickable') or
#                 ex.msg.startswith('Element is not currently visible')
#             ):
#                 logger.debug(
#                     "Element %r is not clickable at this point." % elem)
#                 raise exceptions.ElementIsNotClickableError(str(ex))
#             raise
#
#     def click(elem):
#         ApplicationStatus(elem.parent).wait_until_ready()
#         WebDriverWait(
#             elem,
#             CLICK_TIMEOUT,
#             ignored_exceptions=(exceptions.ElementIsNotClickableError,)
#         ).until(
#             lambda el: _click_if_clickable(elem=el) is None
#         )
#
#     setattr(webelement.WebElement, 'click', click)
#
# __patch_element_click()
#


# import base64
# def __save_screen_on_except(self, exception):
#         """Save screenshot returned in risen WebDriver exception.
#
#         Parameters
#         ----------
#         exception
#             Exception instance.
#
#         Returns
#         -------
#         bool
#             True on success or False on error or no screenshot to save.
#         """
#         try:
#             if exception.screen:
#                 try:
#                     filename = self.get_screen_filename()
#                     with open(filename, 'wb') as fh:
#                         fh.write(base64.decodestring(exception.screen))
#                     logger.info("Screenshot saved: %s (%d bytes)"
#                                 % (filename, len(exception.screen)))
#                 except IOError as ex:
#                     logger.error("Failed to save screenshot: %s" % ex)
#                     return False
#         except AttributeError:
#             return False
#         return True
