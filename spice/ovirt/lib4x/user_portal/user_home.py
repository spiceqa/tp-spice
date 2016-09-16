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
import time

from selenium.webdriver.common import by

from .. import page_base
from .. import dialogs
from .. import excepts
from .. import elements

from . import basictab
from . import extendedtab

logger = logging.getLogger(__name__)

TIMEOUT_HOME_PAGE = 45


class UserHomePageModel(page_base.PageModel):
    username = elements.PageElement(by.By.ID, 'HeaderView_userName')
    sign_out_link = elements.PageElement(by.By.ID, 'HeaderView_logoutLink')
    guide_link = elements.PageElement(by.By.ID, 'HeaderView_guideLink')
    about_link = elements.PageElement(by.By.ID, 'HeaderView_aboutLink')
    basic_tab = elements.PageElement(by.By.CSS_SELECTOR, 'a[href=\#basic]')
    extended_tab = elements.PageElement(by.By.CSS_SELECTOR,
                                        'a[href=\#extended-vm]')


class UserAboutDlgModel(page_base.PageModel):
    close_btn = elements.Button(by.By.XPATH,
                            '//div[@role="button"][starts-with(., "Close")]')
    title = elements.PageElement(
        by.By.XPATH,
        '//div[starts-with(@class, "gwt-DialogBox")]'
        '//div[contains(@class, "gwt-Label")][text()="About"]')


class UserHomePage(page_base.PageObject):
    """Home page abstraction class.
    """
    _model = UserHomePageModel
    _label = "user portal home page"
    _timeout = TIMEOUT_HOME_PAGE

    def init_validation(self):
        """Check that user's drop-down menu is present.

        Returns
        -------
        bool
            True - success.
        """
        self._model.username
        return True

    def sign_out_user(self):
        """Sign out by clicking on the user's drop-down menu -> Sign Out.

        Returns
        -------
            LoginPage page object.
        """
        # Lazy import - required to avoid circular import with loginpage module.
        from . import user_login
        self._model.username.click()
        self._model.sign_out_link.click()
        return user_login.UserLoginPage(self.driver)

    def get_user_portal_guide_url(self):
        """Open User Portal Guide documentation in new window/tab,
        read the URL and close it.
        Returns
        -------
            URL of the User Portal Guide.

        Raises
        ------
        UserActionError
            Could not open Guide in a new window/tab.
        """
        window_cnt_before = len(self.driver.window_handles)
        self._model.guide_link.click()
        if len(self.driver.window_handles) == window_cnt_before:
            raise excepts.UserActionError(
                "failed to open User Portal Guide in new window/tab")
        self.driver.switch_to_window(self.driver.window_handles[-1])
        guide_url = self.driver.current_url
        self.driver.close()
        self.driver.switch_to_window(self.driver.window_handles[-1])
        return guide_url

    def open_about_dialog(self):
        """Open the 'About' dialog.

        Returns
        -------
        AboutDialog
            Page object.
        """
        self._model.about_link.click()
        return AboutDialog(self.driver)

    def go_to_basic_tab(self):
        """Go to the Basic tab by clicking on 'Basic' tab label.

        Returns
        -------
        BasicTabCtrl
            Basic tab controller instance on success.
        """
        self._model.basic_tab.click()
        try:
            basictab.BasicTab(self.driver)
        except InitPageValidationError:
            pass
        time.sleep(1)
        self._model.basic_tab.click()
        basictab.BasicTab(self.driver)
        # quick workaround for
        # https://bugzilla.redhat.com/show_bug.cgi?id=1150581
        return basictab.BasicTabCtrl(self.driver)

    def go_to_extended_tab(self):
        """Go to the Extended tab by clicking on 'Extended' tab label.

        Returns
        -------
        ExtendedTab
            Instance on success.
        """
        self._model.extended_tab.click()
        ext_tab = extendedtab.ExtendedTab(self.driver)
        ext_tab.go_to_vms_tab()
        # quick workaround for
        # https://bugzilla.redhat.com/show_bug.cgi?id=1150581
        return extendedtab.ExtendedTabCtrl(self.driver)


class UserAboutDialog(dialogs.ModalDlg):
    """Home page abstraction class.
    """
    _model = UserAboutDlgModel
    _label = "About dialog"

    def init_validation(self):
        """Check that user is logged in ('Sign Out' link is present).

        Returns
        -------
        bool
            True - success.
        """
        self._model.title
        return True

    def close(self):
        """Close dialog.

        Returns
        -------
        bool
            True - success.
        """
        self._model.close_btn.click()
        return True

    @property
    def title(self):
        """About dialog title.
        """
        return self._model.title
