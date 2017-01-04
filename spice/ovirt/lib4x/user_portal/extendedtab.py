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

import re
import time
import logging

from selenium.webdriver.common import by
from selenium import common

from .. import page_base
from .. import elements
from .. import support
from .. import excepts
from .. import vms_base
from .. import dialogs


logger = logging.getLogger(__name__)


TIMEOUT_MAIN_TAB = 30
TIMEOUT_TABLE_ROW = 10


class SideTabModel(page_base.PageModel):
    vms_link = elements.PageElement(by.By.CSS_SELECTOR, 'a[href=\#extended-vm]')
    templates_link = elements.PageElement(
        by.By.CSS_SELECTOR, 'a[href=\#extended-template]')


class VMsTabMenuBarModel(page_base.PageModel):
    """ VMs menu bar. """
    new_vm_btn = elements.Button(
        by.By.ID, 'SideTabExtendedVirtualMachineView_table_NewVm')
    edit_btn = elements.Button(
        by.By.ID, 'SideTabExtendedVirtualMachineView_table_Edit')
    remove_btn = elements.Button(
        by.By.ID, 'SideTabExtendedVirtualMachineView_table_Remove')
    clone_btn = elements.Button(
        by.By.ID, 'SideTabExtendedVirtualMachineView_table_CloneVm')
    run_once_btn = elements.Button(
        by.By.ID, 'SideTabExtendedVirtualMachineView_table_RunOnce')
    change_cd_btn = elements.Button(
        by.By.ID, 'SideTabExtendedVirtualMachineView_table_ChangeCD')
    make_tmpl_btn = elements.Button(
        by.By.ID, 'SideTabExtendedVirtualMachineView_table_NewTemplate')


class VMModel(page_base.TableRowModel):
    """ A single VM instance. """
    _NAME_CELL_XPATH = (
        '//span[starts-with(@id,'
        '"SideTabExtendedVirtualMachineView_table_content_col2_row")]'
        '[text()="%s"]')
    status = elements.DynamicPageElement(
        by.By.ID,
        'SideTabExtendedVirtualMachineView_'
        'table_content_col1_row%s')
    name = elements.DynamicPageElement(
        by.By.ID,
        'SideTabExtendedVirtualMachineView_'
        'table_content_col2_row%s')
    run_btn = elements.DynamicButton(
        by.By.ID,
        'SideTabExtendedVirtualMachineView_'
        'table_content_runButton_row%s')
    shutdown_btn = elements.DynamicButton(
        by.By.ID,
        'SideTabExtendedVirtualMachineView_'
        'table_content_shutdownButton_row%s')
    suspend_btn = elements.DynamicButton(
        by.By.ID,
        'SideTabExtendedVirtualMachineView_'
        'table_content_suspendButton_row%s')
    stop_btn = elements.DynamicButton(
        by.By.ID,
        'SideTabExtendedVirtualMachineView_'
        'table_content_stopButton_row%s')
    reboot_btn = elements.DynamicButton(
        by.By.ID,
        'SideTabExtendedVirtualMachineView_'
        'table_content_rebootColumn_row%s')
    console_btn = elements.DynamicButton(
        by.By.ID,
        'SideTabExtendedVirtualMachineView_'
        'table_content_col4_row%s')
    console_opts_btn = elements.DynamicButton(
        by.By.ID,
        'SideTabExtendedVirtualMachineView_'
        'table_content_col5_row%s')
    STATUS_UP = 'Up'
    STATUS_DOWN = 'Down'
    STATUS_SUSPENDED = 'Suspended'
    STATUS_PAUSED = 'Paused'
    STATUS_BOOTING = 'PoweringUp'


class RunOnceModel(dialogs.OkCancelDlgModel):
    """ Run once dialog """
    boot_options = elements.PageElement(
        by.By.CSS_SELECTOR, "#VmRunOncePopupWidget_generalBootOptionsPanel a")
    linux_boot_options = elements.PageElement(
        by.By.CSS_SELECTOR, "#VmRunOncePopupWidget_linuxBootOptionsPanel a")
    initial_run = elements.PageElement(
        by.By.CSS_SELECTOR, "#VmRunOncePopupWidget_initialRunPanel a")
    display_protocol = elements.PageElement(
        by.By.CSS_SELECTOR, "#VmRunOncePopupWidget_displayProtocolPanel a")
    system = elements.PageElement(
        by.By.CSS_SELECTOR, "#VmRunOncePopupWidget_systemPanel a")

    attach_floppy = elements.Checkbox(by.By.ID, "VmRunOncePopupWidget_attachFloppy")
    attach_floppy_select = elements.Select(by.By.ID,
                                       "VmRunOncePopupWidget_floppyImage")
    attach_cd = elements.Checkbox(by.By.ID, "VmRunOncePopupWidget_attachIso")
    attach_cd_select = elements.Select(by.By.ID, "VmRunOncePopupWidget_isoImage")
    run_stateless = elements.Checkbox(by.By.ID, "VmRunOncePopupWidget_runAsStateless")
    start_in_pause_mode = elements.Checkbox(by.By.ID,
                                        "VmRunOncePopupWidget_runAndPause")

    kernel_path = elements.TextInput(by.By.ID, "VmRunOncePopupWidget_kernelPath")
    initrd_path = elements.TextInput(by.By.ID, "VmRunOncePopupWidget_initrdPath")
    kernel_params = elements.TextInput(by.By.ID,
                                   "VmRunOncePopupWidget_kernelParameters")

    use_cloud_init = elements.Checkbox(
        by.By.ID, "VmRunOncePopupWidget_cloudInitEnabledEditor")
    vm_hostname = elements.TextInput(
        by.By.ID, "VmRunOncePopupWidget_vmInit_hostnameEditor")
    check_time_zone = elements.Checkbox(
        by.By.ID, "VmRunOncePopupWidget_vmInit_timeZoneEnabledEditor")
    pick_time_zone = elements.Select(
        by.By.ID, "VmRunOncePopupWidget_vmInit_timeZoneEditor")
    authentication_unpack = elements.PageElement(
        by.By.XPATH, '//span[text()="Authentication"]')
    passwd_already_set = elements.Checkbox(
        by.By.ID, "VmRunOncePopupWidget_vmInit_passwordSetEditor")
    root_passwd = elements.TextInput(
        by.By.ID, "VmRunOncePopupWidget_vmInit_rootPasswordEditor")
    root_passwd_confirmation = elements.TextInput(
        by.By.ID, "VmRunOncePopupWidget_vmInit_rootPasswordVerificationEditor")
    ssh_authorized_keys = elements.TextInput(
        by.By.ID, "VmRunOncePopupWidget_vmInit_authorizedKeysEditor")
    regenerate_ssh_keys = elements.Checkbox(
        by.By.ID, "VmRunOncePopupWidget_vmInit_regenerateKeysEnabledEditor")
    networks_unpack = elements.PageElement(
        by.By.XPATH, '//span[text()="Networks"]')
    dns_servers = elements.TextInput(
        by.By.ID, "VmRunOncePopupWidget_vmInit_dnsServers")
    dns_search_domains = elements.TextInput(
        by.By.ID, "VmRunOncePopupWidget_vmInit_dnsSearchDomains")
    network = elements.Checkbox(
        by.By.ID, "VmRunOncePopupWidget_vmInit_networkEnabledEditor")
    network_list = elements.Select(
        by.By.ID, "VmRunOncePopupWidget_vmInit_networkListEditor")
    use_dhcp = elements.Checkbox(
        by.By.ID, "VmRunOncePopupWidget_vmInit_networkDhcpEditor")
    ip_address = elements.TextInput(
        by.By.ID, "VmRunOncePopupWidget_vmInit_networkIpAddressEditor")
    netmask = elements.TextInput(
        by.By.ID, "VmRunOncePopupWidget_vmInit_networkNetmaskEditor")
    gateway = elements.TextInput(
        by.By.ID, "VmRunOncePopupWidget_vmInit_networkGatewayEditor")
    start_on_boot = elements.Checkbox(
        by.By.ID, "VmRunOncePopupWidget_vmInit_networkStartOnBootEditor")
    custom_script_unpack = elements.PageElement(
        by.By.XPATH, '//span[text()="Custom Script"]')
    custom_script = elements.TextInput(
        by.By.ID, "VmRunOncePopupWidget_vmInit_customScriptEditor")

    display_console_vnc = elements.Radio(
        by.By.ID, "VmRunOncePopupWidget_displayConsoleVnc")
    display_console_spice = elements.Radio(
        by.By.ID, "VmRunOncePopupWidget_displayConsoleSpice")
    vnc_keyboard_layout = elements.Select(
        by.By.ID, "VmRunOncePopupWidget_vncKeyboardLayout")

    ok_btn = elements.Button(by.By.ID, "VmRunOncePopupView_OnRunOnce")
    cancel_btn = elements.Button(by.By.ID, "VmRunOncePopupView_Cancel")


class ChangeCDModel(dialogs.OkCancelDlgModel):
    """Change CD dialog """
    pick_cd = elements.Select(
        by.By.ID, "VmChangeCDPopupWidget_isoImage")
    ok_btn = elements.Button(
        by.By.ID, "VmChangeCDPopupView_OnChangeCD")
    cancel_btn = elements.Button(
        by.By.ID, "VmChangeCDPopupView_Cancel")


class TemplateTabMenuBarModel(page_base.PageModel):
    edit_btn = elements.Button(
        by.By.ID, "SideTabExtendedTemplateView_table_Edit")
    remove_btn = elements.Button(
        by.By.ID, "SideTabExtendedTemplateView_table_Remove")


class TemplateModel(page_base.TableRowModel):
    """Single template instance.
    """
    _NAME_CELL_XPATH = (
        '//span[starts-with(@id,"SideTabExtendedTemplateView'
        '_table_content_name_row")]'
        '[text()="%s"]')
    name = elements.DynamicPageElement(
        by.By.ID, "SideTabExtendedTemplateView_table_content_name_row%s")
    version = elements.DynamicPageElement(
        by.By.ID, "SideTabExtendedTemplateView_table_content_col2_row%s")
    sub_version = elements.DynamicPageElement(
        by.By.ID, "SideTabExtendedTemplateView_table_content_col3_row%s")
    description = elements.DynamicPageElement(
        by.By.ID, "SideTabExtendedTemplateView_table_content_col4_row%s")


class VMsSubTabModel(page_base.PageModel):
    general_tab_link = elements.PageElement(
        by.By.CSS_SELECTOR, 'a[href="#extended-vm-general"]')
    net_ifaces_tab_link = elements.PageElement(
        by.By.CSS_SELECTOR, 'a[href="#extended-vm-network_interfaces"]')
    disks_tab_link = elements.PageElement(
        by.By.CSS_SELECTOR, 'a[href="#extended-vm-disks"]')
    snapshots_tab_link = elements.PageElement(
        by.By.CSS_SELECTOR, 'a[href="#extended-vm-snapshots"]')
    permissions_tab_link = elements.PageElement(
        by.By.CSS_SELECTOR, 'a[href="#extended-vm-permissions"]')
    events_tab_link = elements.PageElement(
        by.By.CSS_SELECTOR, 'a[href="#extended-vm-events"]')
    apps_tab_link = elements.PageElement(
        by.By.CSS_SELECTOR, 'a[href="#extended-vm-applications"]')
    monitor_tab_link = elements.PageElement(
        by.By.CSS_SELECTOR, 'a[href="#extended-vm-monitor"]')
    sessions_tab_link = elements.PageElement(
        by.By.CSS_SELECTOR, 'a[href="#extended-vm-sessions"]')


class VDisksTabModel(page_base.PageModel):
    add_btn = elements.Button(
        by.By.ID, 'SubTabExtendedVmVirtualDiskView_table_New')
    edit_btn = elements.Button(
        by.By.ID, 'SubTabExtendedVmVirtualDiskView_table_Edit')
    remove_btn = elements.Button(
        by.By.ID, 'SubTabExtendedVmVirtualDiskView_table_Remove')
    activate_btn = elements.Button(
        by.By.ID, 'SubTabExtendedVmVirtualDiskView_table_Plug')
    deactivate_btn = elements.Button(
        by.By.ID, 'SubTabExtendedVmVirtualDiskView_table_Unplug')
    disk_type_all = elements.Radio(
        by.By.XPATH, '(//input[@name="diskTypeView"])[1]')
    disk_type_image = elements.Radio(
        by.By.XPATH, '(//input[@name="diskTypeView"])[2]')
    disk_type_lun = elements.Radio(
        by.By.XPATH, '(//input[@name="diskTypeView"])[3]')


class VDiskImgInstModel(page_base.TableRowModel):
    _NAME_CELL_XPATH = (
        '//div[starts-with(@id, '
        '"SubTabExtendedVmVirtualDiskView_table_content_col1")]'
        '[text() = "%s"]')
    alias = elements.DynamicPageElement(
        by.By.ID, 'SubTabExtendedVmVirtualDiskView_table_content_col1_row%d')
    vsize = elements.DynamicPageElement(
        by.By.ID, 'SubTabExtendedVmVirtualDiskView_table_content_col6_row%d')
    allocation = elements.DynamicPageElement(
        by.By.ID, 'SubTabExtendedVmVirtualDiskView_table_content_col8_row%d')
    storage_domain = elements.DynamicPageElement(
        by.By.ID, 'SubTabExtendedVmVirtualDiskView_table_content_col9_row%d')
    attached_to = elements.DynamicPageElement(
        by.By.ID, 'SubTabExtendedVmVirtualDiskView_table_content_col16_row%d')
    interface = elements.DynamicPageElement(
        by.By.ID, 'SubTabExtendedVmVirtualDiskView_table_content_col17_row%d')
    alignment = elements.DynamicPageElement(
        by.By.ID, 'SubTabExtendedVmVirtualDiskView_table_content_col18_row%d')
    status = elements.DynamicPageElement(
        by.By.ID, 'SubTabExtendedVmVirtualDiskView_table_content_col19_row%d')
    STATUS_OK = 'OK'


class VDiskPopup(dialogs.OkCancelDlgModel):
    ok_btn = elements.Button(
        by.By.ID, 'VmDiskPopupView_OnSave')
    cancel_btn = elements.Button(
        by.By.ID, 'VmDiskPopupView_Cancel')
    size = elements.TextInput(
        by.By.ID, 'VmDiskPopupWidget_size')
    alias = elements.TextInput(
        by.By.ID, 'VmDiskPopupWidget_alias')
    description = elements.TextInput(
        by.By.ID, 'VmDiskPopupWidget_description')
    interface = elements.Select(
        by.By.ID, 'VmDiskPopupWidget_interface')
    allocation_format = elements.Select(
        by.By.ID, 'VmDiskPopupWidget_volumeType')
    data_center = elements.Select(
        by.By.ID, 'VmDiskPopupWidget_dataCenter')
    storage_domain = elements.Select(
        by.By.ID, 'VmDiskPopupWidget_storageDomain')
    wipe_chk = elements.Checkbox(
        by.By.ID, 'VmDiskPopupWidget_wipeAfterDelete')
    is_bootable_chk = elements.Checkbox(
        by.By.ID, 'VmDiskPopupWidget_isBootable')
    is_shareable_chk = elements.Checkbox(
        by.By.ID, 'VmDiskPopupWidget_isShareable')


class VDiskRemovePopup(dialogs.RemoveConfirmDlg):
    remove_permanently_chk = elements.Checkbox(
        by.By.ID, "RemoveConfirmationPopupView_latch")
    ok_btn = elements.Button(
        by.By.ID, "RemoveConfirmationPopupView_OnRemoveDisk")
    cancel_btn = elements.Button(
        by.By.ID, "RemoveConfirmationPopupView_CancelRemoveDisk")


class ExtendedTab(page_base.PageObject):
    """ General Extended tab page object. """
    _timeout = TIMEOUT_MAIN_TAB
    _model = SideTabModel
    _label = 'Extended tab'

    def init_validation(self):
        """
        Initial validation - check that the Extended tab is displayed.
        """
        self._model.vms_link

    def go_to_vms_tab(self):
        """ Go to the 'Virtual Machines' tab. """
        self._model.vms_link.click()
        return ExtendedTabCtrl(self.driver)  # Is absent in original rhevm-raut

    def go_to_templates_tab(self):
        """ Go to Templates tab """
        self._model.templates_link.click()


class ExtendedTabCtrl(object):

    VM_ACTION_TIMEOUT = 120

    def __init__(self, driver):
        """

        Parameters
        ----------
        driver
            WebDriver instance.
        """
        self.driver = driver

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

    def get_vm_details(self, name):
        """Return VM details.

        Parameters
        ----------
        name
            VM name.

        Returns
        -------
        VMDetailsView
            Instance - success.
        """
        return self._get_vm_inst(name).select()

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

    def get_vm_disk(self, vm_name, disk_name):
        """
        Return
        ------
            VM disks.

        Parameters
        ----------
            Name VM name.

        Returns
        -------
        VDiskInstance
            Instance - success.
        """
        details = self._get_vm_inst(vm_name).select()
        return details.get_disk(disk_name)

    def select_vm(self, name):
        """Select VM.

        Returns
        -------
            VM name.
        """
        vm = self._get_vm_inst(name).select()
        return vm.name

    def run_vm(self, name):
        """Run VM.

        Parameters
        ----------
        name
            VM name.

        Returns
        -------
        bool
            True - success
        """
        vm = self._get_vm_inst(name)
        return vm.run()

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

        Returns
        -------
            True - success.
        """
        vm = self._get_vm_inst(name)
        return vm.suspend()

    def suspend_vm_and_wait_until_suspended(self, name, timeout=None):
        """Suspend VM and wait until is suspended.

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
        self.suspend_vm(name)
        return self.wait_until_vm_is_suspended(name, timeout)

    def shutdown_vm(self, name):
        """Shutdown VM.

        Parameters
        ----------
        name
            VM name.

        Returns
        -------
            True - success.
        """
        vm = self._get_vm_inst(name)
        return vm.shutdown()


    def power_off(self, name):
        """Power off VM.

        Parameters
        ----------
        name
            VM name.

        Returns
        -------
            True - success.
        """
        vm = self._get_vm_inst(name)
        return vm.power_off()

    def shutdown_vm_and_wait_until_down(self, name, timeout=None):
        """Shutdown VM and wait until is down.

        Parameters
        ----------
        name
            VM name.
        timeout
            Timeout in [s] to wait.

        Returns
        -------
            True - success.
        """
        self.shutdown_vm(name)
        return self.wait_until_vm_is_down(name, timeout)

    def restart_vm(self, name):
        """Restart VM.

        Parameters
        ----------
        name
            VM name.

        Returns
        -------
        bool
            True - success.
        """
        vm = self._get_vm_inst(name)
        return vm.restart()

    def restart_vm_and_wait_until_up(self, name, timeout=None):
        """Restart VM and wait until status changes to restarting and back to
        up.

        Parameters
        ----------
        name
            VM name.
        timeout
            Timeout in [s] to wait.

        Returns
        -------
        bool
            True - success
        """
        self.restart_vm(name)
        assert self.wait_until_vm_starts_booting(name, timeout)
        return self.wait_until_vm_is_up(name, timeout)

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

    def wait_until_vm_is_up(self, name, timeout=None):
        """Wait until VM is up.

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
        return self._wait_for_vm_status(name, 'is_up', timeout)

    def wait_until_vm_is_suspended(self, name, timeout):
        """Wait until VM is suspended.

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
        return self._wait_for_vm_status(name, 'is_suspended', timeout)

    def wait_until_vm_is_down(self, name, timeout):
        """Wait until VM is down.

        Parameters
        ----------
        name
            VM name
        timeout
            Timeout in [s] to wait.

        Returns
        -------
        bool
            True - success / False - failure.
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


    def get_vms_names(self):
        marker = '//span[starts-with(@id, "SideTabExtendedVirtualMachineView_table_content_col2_row")]'
        vms = self.driver.find_elements(by.By.XPATH, marker)
        vms_names = map(lambda x : getattr(x, 'text'), vms)
        return set(vms_names)


    def get_vm_from_pool(self, pool_name):
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
        vms_before = self.get_vms_names()
        if pool_name not in vms_before:
            msg = "No VMS pool with name: %s." % pool_name
            raise Exception(msg)
        self.run_vm(pool_name)
        # Some dialog could appier
        vms_base.GuestAgentIsNotResponsiveDlg.ok_ignore(self.driver)
        retries_left = 10
        regex = vms_base.mk_pool_regex(pool_name)
        while retries_left:
            retries_left -= 1
            vms_after = self.get_vms_names()
            new_vms = vms_after - vms_before
            if not new_vms:
                time.sleep(1)
                continue
            for vm_name in sorted(new_vms):
                if re.match(regex, vm_name):
                    vm = VM(self.driver, name=vm_name)
                    if vm.is_up or vm.is_booting:
                        logger.info("Found a new active VM from pool %s: %s.",
                                    pool_name, vm_name)
                    return vm


class TemplateTabMenuBar(page_base.PageObject):
    """ Templates menu bar page object """
    _label = "Templates menu bar"
    _model = TemplateTabMenuBarModel
    _timeout = TIMEOUT_MAIN_TAB


    def init_validation(self):
        """ Initial validation - check that menu bar is present """
        self._model.edit_btn

    def edit(self):
        """
        Click on edit button

        Returns:
          - PageObject: Edit template dialog
        """
        self._model.edit_btn.click()
        return vms_base.VMPopup(self.driver)

    def remove(self):
        """
        Click on remove button

        Returns:
          - PageObject: Remove confirmation popup
        """
        self._model.remove_btn.click()
        return dialogs.RemoveConfirmDlg(self.driver)


class Template(page_base.DynamicPageObject):
    """ Page object for a single template instance """
    _label = "template"
    _model = TemplateModel
    _timeout = TIMEOUT_TABLE_ROW

    def init_validation(self):
        """ Initial validation - check if the template instance is present """
        self._model.name

    def select(self):
        """ Select the template """
        try:
            self._model.name.click()
        except common.exceptions.WebDriverException as ex:
            raise excepts.UserActionError(
                "cannot select %s; reason: %s" % (self, ex))

###########

class VMsTabMenuBar(page_base.PageObject):
    """ VMs tab abstraction class. """
    _model = VMsTabMenuBarModel
    _label = 'VMs menu bar'

    def init_validation(self):
        """ Initial validation - check that VMs menu bar is loaded. """
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
        """
        Click on 'Remove' button.
        Return: `RemoveConfirmDlg` instance
        """
        self._model.remove_btn.click()
        return dialogs.RemoveConfirmDlg(self.driver)

    def clone(self):
        """
        Click on 'Clone VM' button.
        Return: `CloneVmDlg' instance
        """
        self._model.clone_btn.click()
        return vms_base.CloneVmDlg(self.driver)

    def run_once(self):
        """
        Click on 'Run Once' button.
        Return: Run Once instance
        """
        self._model.run_once_btn.click()
        return RunOnce(self.driver)

    def change_cd(self):
        """
        Click on 'Change CD' button.
        Return: Change CD instance
        """
        self._model.change_cd_btn.click()
        return ChangeCD(self.driver)

    def make_template(self):
        """
        Click on 'Make Template' button.
        Return: Make Template instance
        """
        self._model.make_tmpl_btn.click()
        return vms_base.NewTemplateDlg(self.driver)


class VM(page_base.DynamicPageObject):
    """ A table row representing a VM instance. """
    _timeout = TIMEOUT_TABLE_ROW
    _model = VMModel
    __ERR_ACTION_MSG = "Cannot %s %s when status is %s"
    _label = 'VM'

    @property
    def name(self):
        """ VM status. """
        return self._model.name.text

    @property
    def status(self):
        """ VM status. """
        return self._model.status.get_attribute('data-status')

    @property
    def is_up(self):
        """ Return whether VM is up. """
        return self.status == self._model.STATUS_UP

    @property
    def is_down(self):
        """ Return whether VM is down. """
        return self.status == self._model.STATUS_DOWN

    @property
    def is_suspended(self):
        """ Return whether VM is suspended. """
        return self.status == self._model.STATUS_SUSPENDED

    @property
    def is_paused(self):
        """Return whether VM is paused.
        """
        return self.status == self._model.STATUS_PAUSED

    @property
    def is_booting(self):
        """Return whether VM is booting.
        """
        return self.status == self._model.STATUS_BOOTING

    def init_validation(self):
        """ Initial validation - check that the VM is present. """
        self._model.name

    def select(self):
        """ Select the VM.

        Return: `VMsSubTab` instance
        """
        self._model.name.click()
        return vms_subtab.VMsSubTab(self.driver)

    def run(self):
        """ Hit the run icon button if the VM state is valid.

        Throws: UserActionError - cannot run VM
        """
        if self.is_suspended or \
                self.is_down or \
                self.status == '':  # VMS pool case (doesn't have status)
            self._model.run_btn.click()
        else:
            raise excepts.UserActionError(
                self.__ERR_ACTION_MSG % ('run', self, self.status))

    def suspend(self):
        """ Hit the suspend icon button if the VM state is valid.

        Throws: UserActionError - cannot suspend VM
        """
        if self.is_up:
            self._model.suspend_btn.click()
        else:
            raise excepts.UserActionError(
                self.__ERR_ACTION_MSG % ('suspend', self, self.status))

    def shutdown(self):
        """ Hit the shutdown icon button if the VM state is valid.

        Throws: UserActionError - cannot shutdown VM
        """
        if self.is_up or self.is_suspended:
            self._model.shutdown_btn.click()
        else:
            raise excepts.UserActionError(
                self.__ERR_ACTION_MSG % ('shutdown', self, self.status))

    def power_off(self):
        """ Hit the power off icon button if the VM state is valid.

        Throws: UserActionError - cannot power_off VM
        """
        if self.is_up or self.is_suspended or self.is_paused:
            self._model.stop_btn.click()
        else:
            raise excepts.UserActionError(
                self.__ERR_ACTION_MSG % ('power_off', self, self.status))

    def console_edit(self):
        """Edit console protocol of VM

        Returns
        -------
            Console Options dialog
        """
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


class RunOnce(dialogs.OkCancelDlg):
    """
    Page object of Run Once dialog
    """
    _model = RunOnceModel
    _label = "Run Once"

    def init_validation(self):
        """ Initial validation, check if dialog is present. """
        self._model.boot_options

    def _fill_boot_options(
            self, attach_floppy, attach_cd, run_stateless,
            start_in_pause_mode):
        self._model.boot_options.click()
        if attach_floppy is not None:
            if attach_floppy:
                self._model.attach_floppy = True
                self._model.attach_floppy_select = attach_floppy
            else:
                self._model.attach_floppy = False
        if attach_cd is not None:
            if attach_cd:
                self._model.attach_cd = True
                self._model.attach_cd_select = attach_cd
            else:
                self._model.attach_cd = False
        self._model.run_stateless = run_stateless
        self._model.start_in_pause_mode = start_in_pause_mode

    def _fill_linux_boot_options(
            self, kernel_path, initrd_path, kernel_params):
        self._model.linux_boot_options.click()
        self._model.kernel_path = kernel_path
        self._model.initrd_path = initrd_path
        self._model.kernel_params = kernel_params

    def _fill_initial_run(
            self, vm_hostname, time_zone, root_passwd,
            ssh_authorized_keys, regenerate_ssh_keys, dns_servers,
            dns_search_domains, ip_address, netmask, gateway,
            start_on_boot, custom_script):
        self._model.initial_run.click()
        self._model.use_cloud_init = True
        self._model.vm_hostname = vm_hostname
        if time_zone is not None:
            if time_zone:
                self._model.check_time_zone = True
                self._model.pick_time_zone = time_zone
            else:
                self._model.check_time_zone = False
        if root_passwd or ssh_authorized_keys or regenerate_ssh_keys:
            self._model.authentication_unpack.click()
            self._model.root_passwd = root_passwd
            self._model.root_passwd_confirmation = root_passwd
            self._model.ssh_authorized_keys = ssh_authorized_keys
            self._model.regenerate_ssh_keys = regenerate_ssh_keys
        if dns_servers or dns_search_domains or ip_address:
            self._model.networks_unpack.click()
            self._model.dns_servers = dns_servers
            self._model.dns_search_domains = dns_search_domains
            self._model.network = True
        if custom_script:
            self._model.custom_script_unpack.click()
            self._model.custom_script = custom_script

    def _fill_display_protocol(self, display_protocol, vnc_kbd):
        self._model.display_protocol.click()
        if display_protocol == "VNC":
            self._model.display_console_vnc.click()
            self._model.vnc_keyboard_layout = vnc_kbd
        elif display_protocol == "SPICE":
            self._model.display_console_spice.click()

    def fill_values(self, attach_floppy=None, attach_cd=None,
                    run_stateless=None, start_in_pause_mode=None,
                    kernel_path=None, initrd_path=None, kernel_params=None,
                    use_cloud_init=None, vm_hostname=None, time_zone=None,
                    root_passwd=None, ssh_authorized_keys=None,
                    regenerate_ssh_keys=None, dns_servers=None,
                    dns_search_domains=None, ip_address=None,
                    netmask=None, gateway=None, start_on_boot=None,
                    custom_script=None, display_protocol=None, vnc_kbd=None):
        """
        Fill out form fields of all given parameters.

        Parameters:
          - attach_floppy (str): bootable floppy name
          - attach_cd (str): bootable cd name
          - run_stateless (bool): run in stateless mode
          - start_in_pause_mode (bool): run VM in pause mode

          - kernel_path (str): path to kernel image
          - initrd_path (str): path to init ramdisk file
          - kernel_params (str): specify kernel params

          - use_cloud_init (bool): use cloud_init for initial run
          - vm_hostname (str): hostname of vm
          - time_zone (str): specify timezone
          - root_passwd (str): set root password
          - ssh_authorized_keys (str): set ssh authorized keys
          - regenerate_ssh_keys (bool): set regeneration of ssh keys
          - dns_servers (str): set dns servers
          - dns_search_domains (str): set dns search domains
          - ip_address (str): set ip address
          - netmask (str): set netmask
          - gateway (str): set gateway
          - start_on_boot (bool): start on boot mode
          - custom_script (str): write custom script

          - display_protocol (str): set display protocol
          - vnc_kbd (str): set keyboard layout
        """
        if not (attach_floppy is attach_cd is
                run_stateless is start_in_pause_mode is None):
            self._fill_boot_options(
                attach_floppy=attach_floppy, attach_cd=attach_cd,
                run_stateless=run_stateless,
                start_in_pause_mode=start_in_pause_mode)

        if not (kernel_path is initrd_path is kernel_params is None):
            self._fill_linux_boot_options(
                kernel_path=kernel_path, initrd_path=initrd_path,
                kernel_params=kernel_params)

        if use_cloud_init is not None:
            self._fill_initial_run(
                vm_hostname=vm_hostname, time_zone=time_zone,
                root_passwd=root_passwd,
                ssh_authorized_keys=ssh_authorized_keys,
                regenerate_ssh_keys=regenerate_ssh_keys,
                dns_servers=dns_servers,
                dns_search_domains=dns_search_domains, ip_address=ip_address,
                netmask=netmask, gateway=gateway, start_on_boot=start_on_boot,
                custom_script=custom_script)

        if not (display_protocol is vnc_kbd is None):
            self._fill_display_protocol(
                display_protocol=display_protocol, vnc_kbd=vnc_kbd)


class ChangeCD(dialogs.OkCancelDlg):
    """ Page object of Change CD dialog """
    _model = ChangeCDModel
    _label = "Change CD"

    def init_validation(self):
        """ Initial validation, check if dialog is present. """
        self._model.pick_cd

    def fill_values(self, cd=None):
        """
        Pick CD to change to

        Parameters:
          - cd (str): name of cd
        """
        self._model.pick_cd = cd



###########

#class VMsSubTab(page_base.PageObject):
#    """
#    General VMs sub-tab page object.
#    """
#    _model = VMsSubTabModel
#    _label = 'VM sub-tabs panel'
#
#    def init_validation(self):
#        """
#        Initial validation.
#        Return: True - successful validation
#        """
#        self._model.general_tab_link
#        return True
#
#    def go_to_disks_sub_tab(self):
#        """
#        Go to `Disks` sub-tab and return its controller.
#        Return:  instance
#        """
#        self._model.disks_tab_link.click()
#        return VDisksSubTabCtrl(self.driver)
#
#    def go_to_snapshots_sub_tab(self):
#        """
#        Go to Snapshots sub-tab and return its controller
#
#        Returns:
#          - snapshot subtab instance (object)
#        """
#        self._model.snapshots_tab_link.click()
#        return snapshots.SnapshotsSubTabCtrl(self.driver)
#        from raut.lib.selenium.ui.common.pages.subtabs.vms import snapshots


#class VDiskImgInstance(disks_common.VDiskImgInstanceBase):
#    """
#    A table row representing an image-based virtual disk instance.
#    """
#    _model = VDiskImgInstModel


#class VDisksSubTab(disks_common.VDisksSubTabBase):
#    """
#    `Disks` sub-tab page object.
#    """
#    _model = VDisksTabModel


#class VDisksSubTabCtrl(disks_common.VDisksSubTabCtrlBase):
#    """
#    `Disks` sub-tab controller. Handles actions
#      like creating, editing and deleting a virtual disk.
#    Parameters:
#        * VDISK_ACTION_TIMEOUT - default timeout for virtual disk actions
#            like `remove_image_disk`
#    """
#    VDISK_ACTION_TIMEOUT = 60
#
#    def __init__(self, driver):
#        """
#        Init.
#        Parameters:
#            * driver - WebDriver instance
#        """
#        self.driver = driver
#        self.vdisks_tab = VDisksSubTab(self.driver)
#
#    def _get_vdisk_img_inst(self, alias):
#        """
#        Return an image-based virtual disk instance (if exists in data grid).
#        Parameters:
#            * alias - virtual disk alias
#        Return: VDiskImgInstance instance - success / None - does not exist
#        """
#        try:
#            vdisk = VDiskImgInstance(self.driver, alias)
#        except excepts.InitPageValidationError:
#            return None
#        else:
#            return vdisk
