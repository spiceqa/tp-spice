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

import logging

from selenium.common import exceptions
from selenium.webdriver.common import by
from selenium.webdriver.support import ui

logger = logging.getLogger(__name__)

# Widget helpers for HTML form elements.


class CheckboxWrapper(object):
    """Checkbox helper, Selenium webelement wrapper.  Provides basic methods
    for manipulation of a checkbox widget.
    """

    def __init__(self, webelement):
        """
        Parameters
        ----------
        webelement
            Element to wrap.

        Raises
        ------
        UnexpectedTagNameException
            Element tag name is not 'INPUT'.
        """
        if webelement.tag_name != "input":
            raise exceptions.UnexpectedTagNameException(
                "Checkbox only works on <input> elements, not on <%s>" %
                webelement.tag_name)
        self._element = webelement

    @property
    def is_checked(self):
        """
        Returns
        -------
        bool
            Whether checkbox is checked or unchecked. True - checked. False -
            unchecked.
        """
        return self._element.is_selected()

    def check(self):
        """Check the checkbox.
        """
        if not self.is_checked:
            self._element.click()

    def uncheck(self):
        """Uncheck the checkbox.
        """
        if self.is_checked:
            self._element.click()

    def do_check(self, to_check):
        """Check or uncheck checkbox according to boolean expression parameter.

        Parameters
        ----------
        to_check : bool
            True - check, False - uncheck, None - do nothing.
        """
        if to_check is not None:
            if to_check:
                self.check()
            else:
                self.uncheck()


class SelectWrapper(ui.Select):
    """A ui.Select element wrapper with extended functionality.
    """

    def select_by_value_starting_with(self, value):
        """Select all options that have a value starting with the `value`
        argument.  That is, when given "foo" this would select options like:

            <option value="foo">Bar</option>
            <option value="foo_bar">Bar</option>
            <option value="foo (Bar)">Bar</option>

        Notes
        -----
        This method is just modified re-implementation of the original
        `Select.select_by_value` method.

        Parameters
        ----------
        value : str
            Start of the value string to match against.
        """
        css = "option[value^=%s]" % self._escapeString(value)
        opts = self._el.find_elements(by.By.CSS_SELECTOR, css)
        matched = False
        for opt in opts:
            self._setSelected(opt)
            if not self.is_multiple:
                return
            matched = True
        if not matched:
            raise exceptions.NoSuchElementException(
                "Cannot locate option starting with value: %s"
                % value)

    def select_by_visible_text_starting_with(self, text):
        """Select all options that the display text starts with the `text`
        argument.  That is, when given "Bar" this would select options like:

            <option value="foo">Bar</option>
            <option value="foo">BarBaz</option>
            <option value="foo"> Bar (Baz)</option>

        Notes
        -----
        This method is just modified re-implementation of the original
        `Select.select_by_visible_text` method.

        Parameters
        ----------
        text : str
            Start of the visible text to match against.
        """
        xpath = (".//option[starts-with(normalize-space(.), %s)]"
                 % self._escapeString(text))
        opts = self._el.find_elements(by.By.XPATH, xpath)
        matched = False
        for opt in opts:
            self._setSelected(opt)
            if not self.is_multiple:
                return
            matched = True
        if not matched:
            raise exceptions.NoSuchElementException(
                "Could not locate option"
                " starting with visible text: %s"
                % text)


class RootPageElement(property):
    """Property of a page model representing a root page element.  If is
    accessed, it returns standard Selenium <WebElement> instance.  This class
    is meant to be used only for root page elements of a page model!  For
    regular elements of a page model, use <*PageElement> classes and
    successors.

    Examples
    --------
    class LoginPageModel(PageModel):
        _root = RootPageElement(by=By.ID, locator='LoginPopupView_loginForm')
    """

    def __init__(self, by, locator):
        """Save locator type and value to attributes.

        Parameters
        ----------
        by :
            Element locator type; see selenium.webdriver.common.by.By.
        locator :
            Element locator value.
        """
        self._by = by
        self._locator = locator
        super(RootPageElement, self).__init__(self._get, self._set)

    def _get(self, model):
        """Property getter method.  The return value is what is returned, when
        a <*PageModel> attribute is accessed.

        Parameters
        ----------
        model :
            <*PageModel> instance.

        Returns
        -------
        xxx
            Selenium <WebElement> instance.
        """
        return model._driver.find_element(by=self._by, value=self._locator)

    def _set(self, model, value):
        """Property setter method. Not implemented for the root page element.
        """
        raise NotImplementedError("Setting value via assignment is not allowed"
                                  " for root page element.")


class PageElement(RootPageElement):
    """Property of a page model representing a general page element.  If is
    accessed, it returns standard Selenium <WebElement> instance or instance of
    a wrapper helper class defined as `_helper` attribute.

    Examples
    --------
    class SelectBox(PageElement):
        _helper = selenium.webdriver.support.ui.Select

        def set_value(self, element, value):
            element.select_by_value(value)

    class LoginPageModel(PageModel):
        username = PageElement(by=By.ID, locator='LoginPopupView_userName')
        domain = SelectBox(by=By.ID, locator='LoginPopupView_domain')

    Attributes
    ----------
    _helper :
        Helper wrapper class, providing extended functionality to a WebElement
        instance.  Example: selenium.webdriver.support.ui.Select.
    _is_dynamic : bool
        Is part of the locator string dynamic and needs to be interpolated?
        false in this case.
    """
    _helper = None
    _is_dynamic = False

    def __init__(self, by, locator, as_list=False):
        """Save arguments to attributes.

        Parameters
        ----------
        by :
            Element locator type; see selenium.webdriver.common.by.By.
        locator :
            Element locator value.
        as_list : bool
            Return single page element or a list of element(s).

        Raises
        ------
        ValueError
            Attempt for using a dynamic element as list.
        """
        super(PageElement, self).__init__(by, locator)
        if self._is_dynamic and as_list:
            raise ValueError("List of page elements cannot be set as dynamic.")
        self._as_list = as_list

    def _get(self, model):
        """Property getter method.
        The return value is what is returned, when a <*PageModel> attribute
        is accessed. If model instance has defined a root element
        (via `_root` attribute), all page elements are looked up
        relatively to the root element.

        Parameters
        ----------
        model :
            <*PageModel> instance.

        Returns
        -------
        xxx
            Selenium <WebElement> instance or instance of a user-defined
            helper.
        """
        root_element = model._root or model._driver
        lookup_method = root_element.find_element
        if self._as_list:
            lookup_method = root_element.find_elements
        locator = self._locator
        if self._is_dynamic:
            locator = self._locator % model._instance_identifier
        webelement = lookup_method(by=self._by, value=locator)
        if self._helper:
            return self._helper(webelement)
        return webelement

    def _set(self, model, value):
        """Property setter method.
        Gets the element via the getter and sets its value via user-defined
        method `set_value`.

        Notes
        -----
            If value is None, no action is performed at all, not even the page
            element lookup! This is useful for completely skipping some
            elements on page when assigning values from external source like
            dictionary or a config file.

        Parameters
        ----------
        model : xxx
            Page model instance (must be a successor of <PageModelBase>).
        value : xxx
            Value to be set.
        """
        if value is not None:
            webelement = self._get(model)
            self.set_value(webelement, value)

    def set_value(self, element, value):
        """User-defined setter method.
        Implement it in a child class only if you want to set a value
        of page element via assignment. Still you can use methods
        provided by the <WebElement> or by defined helper class.

        Parameters
        ----------
        element :
            <WebElement> instance or instance of a user-defined helper.
        value :
            value to be set.

        Raises
        ------
        ValueError
            This base page element cannot be set via assignment.
        """
        raise ValueError('cannot set free-form page element via assignment')


class DynamicPageElement(PageElement):
    """Property of a page model representing a general dynamic page element.
    If is accessed, it returns a <WebElement> instance or instance of a wrapper
    helper class defined as `_helper` attribute.  Dynamic page element suppose
    to have part(s) of the locator string defined for run-time interpolation
    using the '%s' formatter.

    Examples
    --------
    class VMInstanceModel(DynamicPageModel):
        name = DynamicPageElement(by=By.ID, locator='VMList_name_%s')
        status = DynamicPageElement(by=By.ID, locator='VMList_status_%s')

        def _instance_identifier(self):
            # user-defined action, return value(s) will be used
            # for string interpolation of the locator
            return self._name

    vm_mod = VMInstanceModel(driver, 'test-vm-01')


    Attributes
    ----------
    _is_dynamic : bool
        Is part of the locator string dynamic and needs to be interpolated?
        true in this case.
    """
    _is_dynamic = True

    def __init__(self, by, locator):
        """Note that with dynamic page element you cannot return list of
        elements using the `as_list` argument as with static page element.

        Parameters
        ----------
        by:
            Element locator type; see selenium.webdriver.common.by.By
        locator:
            Element locator value.
        """
        super(DynamicPageElement, self).__init__(by=by, locator=locator,
                                                 as_list=False)


class Checkbox(PageElement):
    """Page element for a checkbox widget.
    """
    _helper = CheckboxWrapper

    def set_value(self, element, value):
        """Setter method for handling the widget when using value assignment.

        Parameters
        ----------
        element
            <forms.Checkbox> Selenium helper instance.
        value
            Value used in assignment.  options: True - check; False - uncheck;
            None - do nothing
        """
        element.do_check(value)


class Radio(PageElement):
    """Page element for a radio widget.
    """

    def set_value(self, element, value):
        """Setter method for handling the widget when using value assignment.

        Parameters
        ----------
        element
            Selenium <WebElement> instance.
        value
            Value used in assignment. options: True expression - select radio;
            otherwise do nothing.
        """
        if value:
            element.click()


class Button(PageElement):
    """Page element for a GWT button widget.
    """

    def set_value(self, element, value):
        """Setter method for handling the widget when using value assignment.
        In this case, an attempt to use assignment to a button will fail.

        Raises
        ------
            NotImplementedError - value cannot be assigned to a button.
        """
        raise NotImplementedError("cannot assign value to a button")


class Select(PageElement):
    """Page element for a select box widget.
    """
    _helper = SelectWrapper

    def set_value(self, element, value):
        """Setter method for handling the widget when using value assignment.

        Parameters
        ----------
        element
            <forms.Select> Selenium helper instance.
        value
            Value used in assignment.
        """
        element.select_by_value(str(value))


class LabeledSelect(PageElement):
    """Page element for widget of a select box with label.  This widget is
    mostly used for selecting a cluster, where label shows the data center the
    cluster belongs to.
    """

    def set_value(self, element, value):
        """ Setter method for handling the widget when using value assignment.

        The labeled select is currently implemented as follows:

        <div id="HostPopupView_cluster">  <<<-- this is usually our `element`
          <select>  <<<--- this <select> we want to manage
            <optgroup label="data-center01">
              <option>cluster01</option>
              <option>cluster02</option>
            </optgroup>
          </select>
          <div>
            <label>Data Center: data-center01</label>
          </div>
        </div>

        Parameters
        ----------
        element : WebElement
            WebElement instance, usually a 'div' tag.
        value : str
            Value to be assigned into the widget.
        """
        if element.tag_name.lower() != 'select':
            element = element.find_element_by_tag_name('select')
        select_element = forms.Select(element)
        select_element.select_by_visible_text(str(value))


class TextInput(PageElement):
    """Page element for a text input widget.
    """

    def set_value(self, element, value):
        """Setter method for handling the widget when using value assignment.

        Parameters
        ----------
        element
            Selenium <WebElement> instance.
        value
            Value used in assignment.
        """
        element.clear()
        element.send_keys(value)


PasswordInput = TextInput
TextArea = TextInput


class ComboBox(PageElement):
    """Page element for a combo-box widget.

    Attributes
    ----------
    _KEY_ENTER : unicode
        Enter key representation. The Selenium's `Keys.ENTER` could not be used
        because the widget didn't react to it, so the classic sequence CRLF was
        used.
    """
    _KEY_ENTER = u'\r\n'

    def set_value(self, element, value):
        """Setter method for handling the widget when using value assignment.
        The value is actually assigned to the inner INPUT element.

        Parameters
        ----------
        element : WebElement
            Outter widget element.
        value : str
            value to be assigned.
        """
        input_elem = element.find_element_by_tag_name('input')
        input_elem.clear()
        input_elem.send_keys(value)
        input_elem.send_keys(self._KEY_ENTER)


class DynamicCheckbox(Checkbox):
    """Page element for a dynamic checkbox widget.
    """
    _is_dynamic = True


class DynamicRadio(Radio):
    """Page element for a dynamic radio widget.
    """
    _is_dynamic = True


class DynamicButton(Button):
    """Page element for a dynamic GWT button widget.
    """
    _is_dynamic = True


class DynamicSelect(Select):
    """Page element for a dynamic select box widget.
    """
    _is_dynamic = True


class DynamicTextInput(TextInput):
    """Page element for a dynamic text input widget.
    """
    _is_dynamic = True


DynamicPasswordInput = DynamicTextInput
