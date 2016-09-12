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

import time

#from raut.lib.selenium.ui.webadmin import pages

import page
import dialogs
import element
import exceptions
import basictab
import extendedtab
from selenium.webdriver.common import by

TIME_HOME_PAGE = 45


class AdminHomePage(page.PageObject):
    """
    Page object for homepage and the main tab.
    """
    _model = AdminHomePageModel
    _label = 'webadmin home page & main tab'
    _timeout = TIME_HOME_PAGE

    def init_validation(self):
        """
        Initial validation - check that login form is loaded.
        """
        self._model.logged_user

    def sign_out(self):
        """
        Sign out from RHEVM.
        """
        self._model.sign_out_link.click()

    def go_to_navigation_pane(self):
        """
        Go to the Tree navigation side-pane and unfold it.
        Return: NavigationPaneCtrl instance.
        """
        return pages.navigation.NavigationPaneCtrl(self.driver)

    def go_to_data_centers_tab(self):
        """
        Select Data Centers tab.
        Return: DataCentersController instance.
        """
        self._model.data_centers_link.click()
        return pages.datacenters.DataCentersController(self.driver)

    def go_to_clusters_tab(self):
        """ Select Clusters tab. """
        self._model.clusters_link.click()

    def go_to_hosts_tab(self):
        """ Select Hosts tab. """
        self._model.hosts_link.click()

    def go_to_storage_tab(self):
        """ Select Storage tab. """
        self._model.storage_link.click()

    def go_to_disks_tab(self):
        """ Select Disks tab """
        self._model.disks_link.click()

    def go_to_vms_tab(self):
        """ Select the Virtual Machines tab """
        self._model.vms_link.click()

    def go_to_templates_tab(self):
        """ Select Templates tab """
        self._model.templates_link.click()

    def go_to_quota_tab(self):
        """
        Select Quota tab
        Return: QuotaTabCtrl instance.
        """
        self._model.quota_link.click()
        return pages.quota.QuotaTabCtrl(self.driver)


class AdminHomePageModel(page.PageModel):
    """Page model for homepage & adminportal main tab.
    """
    logged_user = element.PageElement(by.By.ID, 'HeaderView_userName')
    sign_out_link = element.PageElement(by.By.ID, 'HeaderView_logoutLink')
    data_centers_link = element.PageElement(by.By.LINK_TEXT, 'Data Centers')
    clusters_link = element.PageElement(by.By.LINK_TEXT, 'Clusters')
    hosts_link = element.PageElement(by.By.LINK_TEXT, 'Hosts')
    storage_link = element.PageElement(by.By.LINK_TEXT, 'Storage')
    disks_link = element.PageElement(by.By.LINK_TEXT, 'Disks')
    vms_link = element.PageElement(by.By.LINK_TEXT, 'Virtual Machines')
    pools_link = element.PageElement(by.By.LINK_TEXT, 'Pools')
    templates_link = element.PageElement(by.By.LINK_TEXT, 'Templates')
    users_link = element.PageElement(by.By.LINK_TEXT, 'Users')
    quota_link = element.PageElement(by.By.LINK_TEXT, 'Quota')
    events_link = element.PageElement(by.By.LINK_TEXT, 'Events')
