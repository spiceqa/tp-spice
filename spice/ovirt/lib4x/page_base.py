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


"""Classes to work with page abstraction.
"""

import abc
import re
import logging

from selenium.webdriver.common import by
from selenium import common

import excepts

logger = logging.getLogger(__name__)

TIMEOUT_PAGE_OBJECT = 15


class PageObjectBase(object):
    """Abstract base class for page object.

    Parameters
    ----------
    _driver
        Selenium webdriver instance.
    _location
        Default page location; optional if None, no URL is loaded after object
        initialization.
    _timeout
        Implicit timeout in s for all page object instances.
    _model
        Page object model instance, enumerator of page elements and related
        strings.
    _label
        Human-readable label used for PO string representation.
    """
    __metaclass__ = abc.ABCMeta
    _driver = None
    _location = None
    _model = None
    _label = None

    def __init__(self, driver, timeout=None, **kwargs):
        """Init, set implicit timeout for element search, load URL if one is
        given and run init validation, ensuring that we are on the right
        location.

        Parameters
        ----------
        driver
            Webdriver instance.
        kwargs
            Additional arguments, which are passed to <init> method.
        timeout : int, optional
            Timeout for page initialization.
        """
        self._driver = driver
        self._timeout = timeout or TIMEOUT_PAGE_OBJECT
        self._driver.implicitly_wait(self._timeout)
        if self._location:
            self._driver.get(self._location)
        self.init(**kwargs)
        self._initial_page_object_validation()
        self._driver.implicitly_wait(TIMEOUT_PAGE_OBJECT)  # Restore default.

    def __str__(self):
        """Return human readable page object label if available.
        """
        return self._label or '<%s> page object' % self.__class__.__name__

    def __unicode__(self):
        return unicode(str(self))

    def _initial_page_object_validation(self):
        """Calls <init_validation> method and reports all WebDriver and
        ElementDoesNotExistError exceptions as page object validation error.
        """
        try:
            self.init_validation()
        except (common.exceptions.WebDriverException,
                excepts.ElementDoesNotExistError) as ex:
            raise excepts.InitPageValidationError(
                "Could not initialize %s within %d seconds; reason: %s"
                % (self, self._timeout, ex))

    @property
    def driver(self):
        """WebDriver instance property.
        """
        return self._driver

    @property
    def location(self):
        """Page URL property, mostly used for initial loading the page.
        """
        return self._location

    def init(self, **kwargs):
        """Process additional arguments passed from __init__.  This method can
        be overloaded in descendant class for its specific purpose.

        Parameters
        ----------
        kwargs
            Additional arguments passed from __init__.
        """
        pass

    @abc.abstractmethod
    def init_validation(self):
        """Abstract method for mandatory initial page object validation.  This
        method is always called at the end of the __init__ method.  Note: All
        WebDriverException errors in this method are caught automatically and
        an InitPageValidationError is thrown in return.  Other types of
        exceptions must be caught explicitly.  Throws: should be an
        InitPageValidationError in case of error.
        """
        return None

    @property
    def is_present(self):
        """Return whether the page object is present or not.  The page object
        presence is determined by running the initial validation routine.

        Returns
        -------
        bool
            True - is present or False - not present.
        """
        try:
            self._initial_page_object_validation()
        except excepts.InitPageValidationError:
            return False
        return True


class PageObject(PageObjectBase):
    """New-style static page object.
    """

    def __init__(self, driver, **kwargs):
        """Initialize the page object and check the page model class is valid.

        Parameters
        ----------
        driver
            Webdriver instance.
        """
        if not issubclass(self._model, PageModel):
            raise TypeError("page model type mismatch: "
                            "%s class is not subclass of PageModel"
                            % self._model.__name__)
        self._model = self._model(driver)
        super(PageObject, self).__init__(driver, **kwargs)


class DynamicPageObject(PageObjectBase):
    """New-style dynamic page object.  All dynamic page object instances must
    specify its name, according to whose it's possible to identify it.

    Examples
    --------
    class VMInstance(DynamicPageObject):
        ...
        ...

    vm_instance = VMInstance(driver, name='test-vm-01')
    """

    def __init__(self, driver, name):
        """Initialize the page object and check the page model class is valid.

        Parameters
        ----------
        driver
            Webdriver instance.
        name
            Page object name; this value is also passed to the dynamic page
            model initiator as its instance identifier.
        """
        self._name = name
        self._label = '%s %s' % (self._label, name)
        if not issubclass(self._model, DynamicPageModel):
            raise TypeError("page model type mismatch: "
                            "%s class is not subclass of DynamicPageModel"
                            % self._model.__name__)
        self._model = self._model(driver, name)
        super(DynamicPageObject, self).__init__(driver)


class PageModelBase(object):
    """Base class for page models.  A page model is designed as a lower layer
    for page objects, which provides basic functionality over single web page
    or its area by describing its page elements as class attributes.  Along
    with page elements, class attributes can specify other information, like
    string constants, etc.  For usage see <*PageElement> docstring.

    Attributes
    ----------
    _root
        Root page element of a page model. If defined, all other page elements
        are looked up relatively to this root element (i.e., inside of the root
        page element).
    """
    _root = None

    def __init__(self, driver):
        """Save the webdriver instance to attribute.

        Parameters
        ----------
        driver
            Webdriver instance.
        """
        self._driver = driver

    def __str__(self):
        """Return human readable page model representation.
        """
        return 'page model <%s>' % self.__class__.__name__

    def __unicode__(self):
        return unicode(str(self))

    def __repr__(self):
        return str(self)


class PageModel(PageModelBase):
    """Basic (static) page model.  It doesn't differ from its base class, but
    is defined separately so we can distinguish it from the DynamicPageModel
    class.  Static page model contains only static page elements, i.e.,
    <PageElement> instances or its direct descendants.
    """

    def __init__(self, driver):
        """Save the webdriver instance to attribute.

        Parameters
        ----------
        driver
            Webdriver instance.
        """
        super(PageModel, self).__init__(driver)


class DynamicPageModel(PageModelBase):
    """Dynamic page model can contain both - static and dynamic - page
    elements.  It must implement property method `_instance_identifier`, whose
    return value is used for string interpolation of locators of all dynamic
    elements.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, driver, name):
        """Save the webdriver instance to an attribute.

        Parameters
        ----------
        driver
            Webdriver instance.
        name
            Page model instance name; this name is used for identifying single
            instance along others, e.g., single VM in the VM list.
        """
        super(DynamicPageModel, self).__init__(driver)
        self._name = name

    def __str__(self):
        """Return human readable page model representation.
        """
        return '%s "%s"' \
               % (super(DynamicPageModel, self).__str__(), self._name)

    @abc.abstractproperty
    def _instance_identifier(self):
        """Page model instance identifier.  Property method whose return value
        is used for string interpolation of locators of all dynamic elements.

        Raises
        ------
        NotImplementedError
            Abstract property, not implemented.
        """
        raise NotImplementedError("abstract property not implemented")


class TableRowModel(DynamicPageModel):
    """Dynamic page model describing a single table row in data grid.

    Note
    ----
    According to _NAME_CELL_XPATH, _instance_identifier() method finds table
    cell containing the instance name, gets its HTML 'id' attribute and with
    regexp obtains the row index, which is returned.  This index is then used
    in locator string interpolation of every dynamic page element.

    Examples
    --------

      class VMInstanceModel(TableRowModel):
          _NAME_CELL_XPATH = ('//div[starts-with(@id,'
                             '"MainTabVirtualMachineView_table_content_col2")]'
                             '[text()="%s"]')

          name = DynamicPageElement(By.ID,
                          'MainTabVirtualMachineView_table_content_col2_row%s')
          host = DynamicPageElement(By.ID,
                          'MainTabVirtualMachineView_table_content_col3_row%s')
          ...
    """
    _ROW_IDX_RE = re.compile(r'.*_row(?P<row_idx>\d+)$')
    _NAME_CELL_XPATH = None

    def __init__(self, *args, **kwargs):
        """Check that _NAME_CELL_XPATH attribute value is defined.

        Raises
        ------
        ValueError
            _NAME_CELL_XPATH value not defined.
        """
        super(TableRowModel, self).__init__(*args, **kwargs)
        if not self._NAME_CELL_XPATH:
            raise ValueError("%s._NAME_CELL_XPATH value not defined."
                             % self.__class__.__name__)

    @property
    def _name_cell_element(self):
        """Returns web element located by _NAME_CELL_XPATH XPath and name.
        """
        try:
            return self._driver.find_element_by_xpath(self._NAME_CELL_XPATH
                                                      % self._name)
        except TypeError as ex:
            raise ValueError("Error formatting _NAME_CELL_XPATH value: %s"
                             % ex)
        except common.exceptions.NoSuchElementException as ex:
            raise excepts.ElementDoesNotExistError(str(ex))

    @property
    def _instance_identifier(self):
        """Table row idnentifier.  Gets the HTML 'id' attribute of web element
        found by _NAME_CELL_XPATH locator and by regexp  obtains the row index.

        Raises
        ------
        ValueError
            Error in string interpolation of _NAME_CELL_XPATH value.
        ElementDoesNotExistError
            No row instance found by the name.

        Returns
        -------
        int
            Table row index.
        """
        id_attr = None
        while id_attr is None:
            id_attr = self._name_cell_element.get_attribute('id')
        match = re.match(self._ROW_IDX_RE, id_attr)
        if match:
            return int(match.group('row_idx'))
        raise excepts.ElementDoesNotExistError(self)
