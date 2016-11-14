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
import logging

#from raut.lib.selenium.ui.webadmin import pages
from selenium.webdriver.common import by

from .. import dialogs
from .. import support
from .. import elements
from .. import vms_base
from .. import page_base

TIME_HOME_PAGE = 45

logger = logging.getLogger(__name__)


class SearchModel(page_base.PageModel):
    search_input = elements.TextInput(
        by.By.ID, 'SearchPanelView_searchStringInput')
    search_btn = elements.Button(
        by.By.ID, 'SearchPanelView_searchButton')
    bookmark_btn = elements.Button(
        by.By.ID, 'SearchPanelView_bookmarkButton')


class SearchPanel(page_base.PageObject):
    """Search panel abstraction class.
    """
    _model = SearchModel
    _label = 'Search panel'


    @property
    def search_string(self):
        return self._model.search_input.text


    def init_validation(self):
        """Initial validation - check that all Search panel elements are
        present.

        Returns
        -------
        bool
            True - successful validation.
        """
        self._model.search_input
        return True


    def submit_search(self, search_string):
        """Submit a search query.

        Parameters
        ----------
        search_string : str
            Search string.

        Returns
        -------
        bool
            True - success.

        """
        self._model.search_input = search_string
        self._model.search_btn.click()
        return True


class AdminHomePageModel(page_base.PageModel):
    """Page model for homepage & adminportal main tab.
    """
    logged_user = elements.PageElement(
        by.By.ID, 'HeaderView_userName')
    sign_out_link = elements.PageElement(
        by.By.ID, 'HeaderView_logoutLink')
    data_centers_link = elements.PageElement(
        by.By.LINK_TEXT, 'Data Centers')
    clusters_link = elements.PageElement(
        by.By.LINK_TEXT, 'Clusters')
    hosts_link = elements.PageElement(
        by.By.LINK_TEXT, 'Hosts')
    storage_link = elements.PageElement(
        by.By.LINK_TEXT, 'Storage')
    disks_link = elements.PageElement(
        by.By.LINK_TEXT, 'Disks')
    vms_link = elements.PageElement(
        by.By.LINK_TEXT, 'Virtual Machines')
    pools_link = elements.PageElement(
        by.By.LINK_TEXT, 'Pools')
    templates_link = elements.PageElement(
        by.By.LINK_TEXT, 'Templates')
    users_link = elements.PageElement(
        by.By.LINK_TEXT, 'Users')
    quota_link = elements.PageElement(
        by.By.LINK_TEXT, 'Quota')
    events_link = elements.PageElement(
        by.By.LINK_TEXT, 'Events')


class AdminHomePage(page_base.PageObject):
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
        # Lazy import - required to avoid circular import with loginpage module.
        from . import admin_login
        self._model.logged_user.click()
        self._model.sign_out_link.click()
        return admin_login.AdminLoginPage(self.driver)

    def go_to_navigation_pane(self):
        """
        Go to the Tree navigation side-pane and unfold it.
        Return: NavigationPaneCtrl instance.
        """
        return pages.navigation.NavigationPaneCtrl(self.driver)

    def go_to_data_centers_tab(self):
        """Select Data Centers tab.

        Returns
        -------
            DataCentersController instance.
        """
        self._model.data_centers_link.click()
        return pages.datacenters.DataCentersController(self.driver)

    def go_to_clusters_tab(self):
        """Select Clusters tab. """
        self._model.clusters_link.click()

    def go_to_hosts_tab(self):
        """Select Hosts tab. """
        self._model.hosts_link.click()

    def go_to_storage_tab(self):
        """Select Storage tab. """
        self._model.storage_link.click()

    def go_to_disks_tab(self):
        """Select Disks tab """
        self._model.disks_link.click()

    def go_to_vms_tab(self):
        """Select the Virtual Machines tab """
        self._model.vms_link.click()
        return VmsTabCtrl(self.driver)  # Is absent in original rhevm-raut

    def go_to_templates_tab(self):
        """Select Templates tab """
        self._model.templates_link.click()

    def go_to_quota_tab(self):
        """Select Quota tab
        Return: QuotaTabCtrl instance.
        """
        self._model.quota_link.click()
        return pages.quota.QuotaTabCtrl(self.driver)


class VmsTabCtrl(object):

    # For more methods see: ./raut/tests/webadmin/vms.py

    _DLG_DISMISS_TIMEOUT = 30

    def __init__(self, driver):
        """

        Parameters
        ----------
        driver
            WebDriver instance.
        """
        self.driver = driver
        self.menu_bar = VMsTabMenuBar(driver)

    def _get_vm_inst(self, name):
        """Return a VM instance.

        Parameters
        ----------
        name
            VM name.

        Returns
        -------
            VMInstance instance - success.
        """
        return VM(self.driver, name=name)

    def run_vm(self, name):
        """Run VM.

        Parameters
        ----------
        name
            VM name.

        """
        vm = self._get_vm_inst(name)
        vm.select()
        return self.menu_bar.run()


    def run_vm_and_wait_until_up(self, name, timeout=None):
        """Run VM and wait until is up.

        Parameters
        ----------
        name
            VM name.
        timeout
            Timeout in [s] to wait.

        Returns
        -------
        bool
            True - success.
        """
        self.run_vm(name)
        return self.wait_until_vm_is_up(name, timeout)


    def suspend_vm(self, name):
        """Suspend VM.

        Parameters
        ----------
        name
            VM name.

        """
        vm = self._get_vm_inst(name)
        vm.select()
        return self.menu_bar.suspend()


    def shutdown_vm(self, name):
        """Shutdown VM.

        Parameters
        ----------
        name
            VM name.

        """
        vm = self._get_vm_inst(name)
        vm.select()
        confirm_dlg = self.menu_bar.shutdown()
        confirm_dlg.submit_and_wait_to_disappear(self._DLG_DISMISS_TIMEOUT)


    def wait_until_vm_is_up(self, name, timeout):
        """Wait until VM status is 'Up'.

        Parameters
        ----------
        name
            VM name.

        """
        vm = self._get_vm_inst(name)
        vm.select()
        support.WaitForPageObject(vm, timeout).status('is_up')


    def wait_until_vm_is_suspended(self, name, timeout):
        """Wait until VM status is 'Suspended'.

        Parameters
        ----------
        name
            VM name.

        """
        vm = self._get_vm_inst(name)
        vm.select()
        support.WaitForPageObject(vm, timeout).status('is_suspended')


    def wait_until_vm_is_down(self, name, timeout):
        """Wait until VM status is 'Suspended'.

        Parameters
        ----------
        name
            VM name.

        """
        return self._wait_for_vm_status(name, 'is_down', timeout)


    def wait_until_vm_starts_booting(self, name, timeout=None):
        """Wait until VM starts powering up.

        Parameters
        ----------
        name
            VM name.
        timeout
            Timeout in [s] to wait.

        Returns
        -------
        bool
            True - success / False - failure.
        """
        return self._wait_for_vm_status(name, 'is_booting', timeout)

    VM_ACTION_TIMEOUT = 120

    def _wait_for_vm_status(self, name, status_prop, timeout=None):
        """Wait until VM status property returns True.

        Parameters
        ----------
        name
            VM name
        status_prop : str
            Name of the status property, e.g. 'vm.is_up' -> 'is_up'
        timeout
            Timeout in [s] to wait.

        Returns
        -------
        bool
            True - success.

        Raises
        ------
        WaitTimeoutError
            Failure.

        """
        vm = self._get_vm_inst(name)
        timeout = timeout or self.VM_ACTION_TIMEOUT
        try:
            w = support.WaitForPageObject(vm, timeout)
            w.status(status_prop)
        except common.exceptions.TimeoutException:
            prop_val = getattr(vm, status_prop)
            msg = "%s.%s is: %s" % (vm.name, status_prop, attr_val)
            raise excepts.WaitTimeoutError(msg)


    def get_vm(self, name):
        """Return VM object.

        Parameters
        ----------
        name
            VM name.

        Returns
        -------
        VMDetailsView
            Instance - success.
        """
        return self._get_vm_inst(name)


    def console(self, name):
        """Invoke console for VM.

        Parameters
        ----------
        name
            VM name.

        """
        vm = self._get_vm_inst(name)
        vm.select()
        confirm_dlg = self.menu_bar.console()


    def console_edit(self, name):
        """Invoke console optiosn for VM.

        Parameters
        ----------
        name
            VM name.

        Returns
        -------
        VMDetailsView
            Instance - success.
        """
        vm = self._get_vm_inst(name)
        vm.select()
        dlg = self.menu_bar.console_edit()
        return dlg


    def get_vms_names(self):
        """Get VMs names.

        Note
        ----
            If there are to much VMs they are not shown all at once. Instead,
            XX per page.
        """
        marker = '//div[starts-with(@id, "MainTabVirtualMachineView_table_content_col2_row")]'
        vms = self.driver.find_elements(by.By.XPATH, marker)
        vms_names = map(lambda x : getattr(x, 'text'), vms)
        return set(vms_names)


    def get_vm_from_pool(self, pool_name):
        search_panel = search.SearchPanel(self.driver)
        search_string = ("Vms: pool={0} and status=up"
                         "or"
                         "pool={0} and status=poweringup" . \
                         format(pool_name))
        search_panel.submit_search(search_string)
        regex = vms_base.mk_pool_regex(pool_name)
        vms = self.get_vms_names()
        for vm_name in sorted(vms):
            if re.match(regex, vm_name):
                vm = VM(self.driver, name=vm_name)
                if vm.is_up or vm.is_booting:
                    logger.info("Found active VM from pool %s: %s.",
                                pool_name,
                                vm_name)
                    return vm
        logger.info("Did not found active vm from pool: %s. Start a new one.",
                    pool_name)
        return self.start_vm_from_pool(self, pool_name)


    def start_vm_from_pool(self, pool_name):
        search_panel = search.SearchPanel(self.driver)
        search_string = ("Vms: pool={0} and status=down" . format(pool_name))
        search_panel.submit_search(search_string)
        vms_before = self.get_vms_names()
        found_free_vm = False
        for vm_name in sorted(vms):
            if re.match(regex, vm_name):
                vm = VM(self.driver, name=vm_name)
                if vm.is_down:
                    logger.info("Found inactive VM from pool %s: %s.",
                                pool_name,
                                vm_name)
                    found_free_vm = True
                    break
        if not found_free_vm:
            msg = "Cannot find free(down) vm from pool: %s." % pool_name
            raise Exception(msg)
        self.run_vm(vm.name)
        self.wait_until_vm_starts_booting(vm.name)
        # Some dialog could appier
        vms_base.GuestAgentIsNotResponsiveDlg.ok_ignore(self.driver)
        return vm

#
# Virtual Machines tab.

# Next goes two files copied from rhevm-raut:
#
#   ./raut/lib/selenium/ui/webadmin/models/vms.py
#   ./raut/lib/selenium/ui/webadmin/pages/vms.py
#

class VMsTabMenuBarModel(page_base.PageModel):
    """ Virtual Machines tab - menu bar. """
    new_vm_btn = elements.Button(
        by.By.ID, 'MainTabVirtualMachineView_table_NewVm')
    edit_btn = elements.Button(
        by.By.ID, 'MainTabVirtualMachineView_table_Edit')
    remove_btn = elements.Button(
        by.By.ID, 'MainTabVirtualMachineView_table_Remove')
    clone_btn = elements.Button(
        by.By.ID, 'MainTabVirtualMachineView_table_CloneVm')
    run_btn = elements.Button(
        by.By.ID, 'MainTabVirtualMachineView_table_Run')
    suspend_btn = elements.Button(
        by.By.ID, 'MainTabVirtualMachineView_table_Pause')
    shutdown_btn = elements.Button(
        by.By.ID, 'MainTabVirtualMachineView_table_Shutdown')
    make_template_btn = elements.Button(
        by.By.ID, 'MainTabVirtualMachineView_table_NewTemplate')
    # SpiceQE:
    reboot_btn = elements.Button(
        by.By.ID, 'MainTabVirtualMachineView_table_Reboot')
    migrate_btn = elements.Button(
        by.By.ID, 'MainTabVirtualMachineView_table_Migrate')
    # Activate console.
    console_btn = elements.Button(
        by.By.XPATH, '//div[starts-with(@id, "MainTabVirtualMachineView_table_ConsoleConnectCommand")]/div/div[1]')
    # Navigate to console options.
    console_opts = elements.Button(
        by.By.XPATH, '//div[starts-with(@id, "MainTabVirtualMachineView_table_ConsoleConnectCommand")]/div/div[2]')
    # "Console Options".
    console_opts_btn = elements.Button(
        by.By.CLASS_NAME , 'actionPanelPopupMenuBar')


class VMModel(page_base.TableRowModel):
    """ VM instance model. """
    _NAME_CELL_XPATH = ('//div[starts-with(@id,'
                        '"MainTabVirtualMachineView_table_content_col2")]'
                        '[text() = "%s"]')
    name = elements.DynamicPageElement(
        by.By.ID, 'MainTabVirtualMachineView_table_content_col2_row%d')
    host = elements.DynamicPageElement(
        by.By.ID, 'MainTabVirtualMachineView_table_content_col4_row%d')
    ip_address = elements.DynamicPageElement(
        by.By.ID, 'MainTabVirtualMachineView_table_content_col5_row%d')
    cluster = elements.DynamicPageElement(
        by.By.ID, 'MainTabVirtualMachineView_table_content_col7_row%d')
    data_center = elements.DynamicPageElement(
        by.By.ID, 'MainTabVirtualMachineView_table_content_col8_row%d')
    display = elements.DynamicPageElement(
        by.By.ID, 'MainTabVirtualMachineView_table_content_col12_row%d')
    status = elements.DynamicPageElement(
        by.By.ID, 'MainTabVirtualMachineView_table_content_col13_row%d')
    # static strings
    STATUS_UP = 'Up'
    STATUS_SUSPENDED = 'Suspended'
    STATUS_DOWN = 'Down'


class VMShutdownConfirmDlgModel(dialogs.OkCancelDlgModel):
    """ Shutdown VM confirmation dialog. """
    ok_btn = elements.Button(
        by.By.ID, 'RemoveConfirmationPopupView_OnShutdown')
    cancel_btn = elements.Button(
        by.By.ID, 'RemoveConfirmationPopupView_Cancel')


TABLE_ROW = 10

class VM(page_base.DynamicPageObject):
    """ A table row representing a VM instance. """
    _timeout = TABLE_ROW
    _model = VMModel
    _label = 'VM'

    def init_validation(self):
        """ Initial validation - check that VM name element is present. """
        self._model.name

    @property
    def status(self):
        """ VM status text. """
        return self._model.status.text

    @property
    def is_up(self):
        """ Return whether VM is Up. """
        return self.status == self._model.STATUS_UP

    @property
    def is_down(self):
        """ Return whether VM is Down. """
        return self.status == self._model.STATUS_DOWN

    @property
    def is_suspended(self):
        """ Return whether VM is Suspended. """
        return self.status == self._model.STATUS_SUSPENDED

    def select(self):
        """ Select the VM.

        Return: `VMsSubTab` instance
        """
        self._model.name.click()
    #     return vms_subtab.VMsSubTab(self.driver)  # XXX TODO


class VMShutdownConfirmDlg(dialogs.OkCancelDlg):
    """ Shut down VM confirmation dialog. """
    _model = VMShutdownConfirmDlgModel
    _label = 'Shut down Virtual Machine(s) dialog'


class VMsTabMenuBar(page_base.PageObject):
    """ Virtual Machines tab - menu bar """
    _model = VMsTabMenuBarModel
    _label = 'Virtual Machines tab - menu bar'

    def init_validation(self):
        """ Initial validation - check that VM tab is present on page. """
        self._model.new_vm_btn

    def new_vm(self):
        """ Click on 'New VM' button.

        Return: `VMPopup` instance
        """
        self._model.new_vm_btn.click()
        return vms_base.VMPopup(self.driver)

    def edit(self):
        """ Click on 'Edit' button.

        Return: `VMPopup` instance
        """
        self._model.edit_btn.click()
        return vms_base.VMPopup(self.driver)

    def remove(self):
        """ Click on 'Remove' button.

        Return: `RemoveConfirmDlg` instance
        """
        self._model.remove_btn.click()
        return dialogs.RemoveConfirmDlg(self.driver)

    def clone(self):
        """
        Click on 'Clone VM' button.

        Return: `CloneVmDlg` instance
        """
        self._model.clone_btn.click()
        return vms_base.CloneVmDlg(self.driver)

    def run(self):
        """ Click on 'Run' button. """
        self._model.run_btn.click()

    def suspend(self):
        """ Click on 'Suspend' button. """
        self._model.suspend_btn.click()

    def shutdown(self):
        """ Click on 'Shut down' button.

        Return: `VMShutdownConfirmDlg` instance
        """
        self._model.shutdown_btn.click()
        return VMShutdownConfirmDlg(self.driver)

    def make_template(self):
        """ Click on 'Make Template' button.

        Return: `NewTemplateDlg` instance
        """
        self._model.make_template_btn.click()
        return vms_base.NewTemplateDlg(self.driver)

    def console_edit(self):
        """Edit console protocol of VM

        Returns
        -------
            Console Options dialog
        """
        self._model.console_opts.click()
        self._model.console_opts_btn.click()
        return vms_base.EditConsoleOptions(self.driver)

    def console(self):
        """Invoke console for VM.

        Returns
        -------
            Console Options dialog
        """
        self._model.console_btn.click()
        time.sleep(3)  # Pause to save .vv file or auto-open it.




# VMS_subtab
# from raut.lib.selenium.ui.webadmin.pages.subtabs import vms as vms_subtab

# Next was generated by:
# cat ./raut/lib/selenium/ui/webadmin/models/subtabs/vms/disks.py
#     ./raut/lib/selenium/ui/webadmin/models/subtabs/vms/__init__.py
#     ./raut/lib/selenium/ui/webadmin/pages/subtabs/vms/disks.py
#     ./raut/lib/selenium/ui/webadmin/pages/subtabs/vms/__init__.py

# from raut.core import By, PageModel, DynamicPageElement
# from raut.lib.selenium.ui.common.models import form, tables
# 
# 
# class VDisksTab(PageModel):
#     """ Disks subtab menu bar page model"""
#     add_btn = form.Button(
#         By.ID, 'SubTabVirtualMachineVirtualDiskView_table_New')
#     edit_btn = form.Button(
#         By.ID, 'SubTabVirtualMachineVirtualDiskView_table_Edit')
#     remove_btn = form.Button(
#         By.ID, 'SubTabVirtualMachineVirtualDiskView_table_Remove')
#     activate_btn = form.Button(
#         By.ID, 'SubTabVirtualMachineVirtualDiskView_table_Plug')
#     deactivate_btn = form.Button(
#         By.ID, 'SubTabVirtualMachineVirtualDiskView_table_Unplug')
#     move_btn = form.Button(
#         By.ID, 'SubTabVirtualMachineVirtualDiskView_table_Move')
#     disk_type_all = form.Radio(By.XPATH, '(//input[@name="diskTypeView"])[1]')
#     disk_type_image = form.Radio(
#         By.XPATH, '(//input[@name="diskTypeView"])[2]')
#     disk_type_lun = form.Radio(By.XPATH, '(//input[@name="diskTypeView"])[3]')
# 
# 
# class VDiskImgInst(tables.TableRowModel):
#     """ Virtual disk page model """
#     _NAME_CELL_XPATH = (
#         '//div[starts-with(@id, '
#         '"SubTabVirtualMachineVirtualDiskView_table_content_col1")]'
#         '[text() = "%s"]')
#     alias = DynamicPageElement(
#         By.ID, 'SubTabVirtualMachineVirtualDiskView_table_content_col1_row%d')
#     vsize = DynamicPageElement(
#         By.ID, 'SubTabVirtualMachineVirtualDiskView_table_content_col6_row%d')
#     allocation = DynamicPageElement(
#         By.ID, 'SubTabVirtualMachineVirtualDiskView_table_content_col8_row%d')
#     storage_domain = DynamicPageElement(
#         By.ID, 'SubTabVirtualMachineVirtualDiskView_table_content_col9_row%d')
#     attached_to = DynamicPageElement(
#         By.ID, 'SubTabVirtualMachineVirtualDiskView_table_content_col16_row%d')
#     interface = DynamicPageElement(
#         By.ID, 'SubTabVirtualMachineVirtualDiskView_table_content_col17_row%d')
#     alignment = DynamicPageElement(
#         By.ID, 'SubTabVirtualMachineVirtualDiskView_table_content_col18_row%d')
#     status = DynamicPageElement(
#         By.ID, 'SubTabVirtualMachineVirtualDiskView_table_content_col19_row%d')
#     STATUS_OK = 'OK'
# from raut.core import By, PageModel, PageElement
# 
# 
# class VMSubtabsPanel(PageModel):
#     general_tab_link = PageElement(By.XPATH, '//a[@href="#vms-general"]')
#     net_ifaces_tab_link = PageElement(
#         By.XPATH, '//a[@href="#vms-network_interfaces"]')
#     disks_tab_link = PageElement(By.XPATH, '//a[@href="#vms-disks"]')
#     snapshots_tab_link = PageElement(By.XPATH, '//a[@href="#vms-snapshots"]')
#     apps_tab_link = PageElement(By.XPATH, '//a[@href="#vms-applications"]')
#     permissions_tab_link = PageElement(
#         By.XPATH, '//a[@href="#vms-permission"]')
# """
# Page objects and controllers for `Disks` sub-tab.
# 
# Author: pnovotny
# """
# from utilities.enum import Enum
# 
# import raut.lib.selenium.ui.webadmin.models.subtabs.vms.disks as m_disks
# import raut.lib.selenium.ui.exceptions as ui_exceptions
# import raut.lib.selenium.ui.common.pages.disks as disks_common
# 
# 
# DISK_TYPE = Enum(
#     IMAGE="image",
#     LUN="LUN",
# )
# 
# 
# class VDiskImgInstance(disks_common.VDiskImgInstanceBase):
#     _model = m_disks.VDiskImgInst
# 
# 
# class VDisksSubTab(disks_common.VDisksSubTabBase):
#     """
#     `Disks` sub-tab page object.
#     """
#     _model = m_disks.VDisksTab
# 
# 
# class VDisksSubTabCtrl(disks_common.VDisksSubTabCtrlBase):
#     """
#     `Disks` sub-tab controller. Handles actions
#       like creating, editing and deleting a virtual disk.
#     Parameters:
#         * VDISK_ACTION_TIMEOUT - default timeout for virtual disk actions
#             like `remove_image_disk`
#     """
#     VDISK_ACTION_TIMEOUT = 60
# 
#     def __init__(self, driver):
#         """
#         Init.
#         Parameters:
#             * driver - WebDriver instance
#         """
#         self.driver = driver
#         self.vdisks_tab = VDisksSubTab(self.driver)
# 
#     def _get_vdisk_img_inst(self, alias):
#         """
#         Return an image-based virtual disk instance (if exists in data grid).
#         Parameters:
#             * alias - virtual disk alias
#         Return: VDiskImgInstance instance - success / None - does not exist
#         """
#         try:
#             vdisk = VDiskImgInstance(self.driver, alias)
#         except ui_exceptions.InitPageValidationError:
#             return None
#         else:
#             return vdisk
# """
# Page objects and controllers for general `Virtual Machines` sub-tab.
# 
# Author: pnovotny
# """
# 
# from raut.lib.selenium.ui.common import timeouts
# from raut.lib.selenium.ui.webadmin.pages.subtabs.vms import disks
# from raut.lib.selenium.ui.webadmin.models.subtabs.vms import VMSubtabsPanel
# from raut.core import PageObject
# 
# 
# class VMsSubTab(PageObject):
#     """
#     General VMs sub-tab page object.
#     """
#     _model = VMSubtabsPanel
#     _label = 'VM sub-tabs panel'
#     _timeout = timeouts.SUB_TAB
# 
#     def init_validation(self):
#         """
#         Initial validation.
#         Return: True - successful validation
#         """
#         self._model.general_tab_link
#         return True
# 
#     def go_to_disks_sub_tab(self):
#         """
#         Go to `Disks` sub-tab and return its controller.
#         Return:  instance
#         """
#         self._model.disks_tab_link.click()
#         return disks.VDisksSubTabCtrl(self.driver)
# 

# VMS_subtab END
