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

from .. import deco
from .. import page_base
from .. import elements
from .. import excepts
from .. import vms_base

logger = logging.getLogger(__name__)

TIMEOUT_MAIN_TAB = 30
TIMEOUT_TABLE_ROW = 10


class VMInstModel(page_base.TableRowModel):
    """VM instance model.
    """
    _ROW_IDX_RE = re.compile(r'.*BasicListView_vm(?P<row_idx>\d+)_name$')
    _NAME_CELL_XPATH = ('//div[starts-with(@id, "MainTabBasicListView_vm")]'
                        '[contains(@id, "_name")]'
                        '[text() = "%s"]')
    name = elements.DynamicPageElement(by.By.ID,
                                       'MainTabBasicListView_vm%s_name')
    status = elements.DynamicPageElement(by.By.ID,
                                         'MainTabBasicListView_vm%s_status')
    run_btn = elements.DynamicButton(by.By.ID,
                                     'MainTabBasicListView_vm%s_runButton')
    shutdown_btn = elements.DynamicButton(
        by.By.ID, 'MainTabBasicListView_vm%s_shutdownButton')
    suspend_btn = elements.DynamicButton(
        by.By.ID, 'MainTabBasicListView_vm%s_suspendButton')
    restart_btn = elements.DynamicButton(
        by.By.ID, 'MainTabBasicListView_vm%s_rebootButton')
    STATUS_UP = 'Machine is Ready'
    STATUS_DOWN = 'Machine is Down'
    STATUS_SUSPENDED = 'Suspended'
    STATUS_BOOTING = 'Powering Up'


class VMDetailsModel(page_base.PageModel):
    """VM details view model.
    """
    name = elements.PageElement(by.By.ID, 'MainTabBasicDetailsView_name')
    description = elements.PageElement(by.By.ID,
                                       'MainTabBasicDetailsView_description')
    os = elements.PageElement(by.By.ID, 'MainTabBasicDetailsView_os')
    memory = elements.PageElement(by.By.ID, 'MainTabBasicDetailsView_memory')
    cores = elements.PageElement(by.By.ID,
                                 'MainTabBasicDetailsView_numberOfCores')
    console = elements.PageElement(by.By.ID,
                                   'MainTabBasicDetailsView_protocol')
    connect = elements.PageElement(by.By.ID, 'MainTabBasicDetailsView_'
                                   'consoleConnectAnchor')
    console_edit = elements.PageElement(
        by.By.ID, 'MainTabBasicDetailsView_editProtocolLink')


class VDiskInstModel(page_base.TableRowModel):
    """VDisk instance model.
    """
    _ROW_IDX_RE = re.compile(
        r'.*DetailsView_disks_disk(?P<row_idx>\d+)_diskName$')
    _NAME_CELL_XPATH = (
        '//div[starts-with(@id, "MainTabBasicDetailsView_disks_disk")]'
        '[contains(@id, "Name")]'
        '[text() = "%s:"]')
    alias = elements.DynamicPageElement(
        by.By.ID, 'MainTabBasicDetailsView_disks_disk%s_diskName')
    size = elements.DynamicPageElement(
        by.By.ID, 'MainTabBasicDetailsView_disks_disk%s_diskSize')


class BasicTab(page_base.PageObject):
    """Basic tab page object - just for checking that basic tab is loaded Using
    model of VMInst because we don't need more than that.
    """
    _timeout = TIMEOUT_MAIN_TAB
    _model = VMDetailsModel
    _label = 'BasicTab'

    def init_validation(self):
        """Initial validation - check that Basic tab has already been loaded.

        Returns
        -------
        bool
            True - successful validation.
        """
        self._model.name
        return True


class VMInstance(page_base.DynamicPageObject):
    """A table row representing a VM instance.
    """
    _timeout = TIMEOUT_TABLE_ROW
    _model = VMInstModel
    _label = 'VM'

    @property
    def name(self):
        """VM name.
        """
        return self._model.name.text

    @property
    def status(self):
        """VM status.
        """
        return self._model.status.text

    def init_validation(self):
        """Initial validation - check that VM instance is present.

        Returns
        -------
        bool
            True - successful validation.
        """
        self._model.name
        return True

    @property
    def is_up(self):
        """Return whether VM is up.
        """
        return self.status == self._model.STATUS_UP

    @property
    def is_down(self):
        """Return whether VM is down.
        """
        return self.status == self._model.STATUS_DOWN

    @property
    def is_suspended(self):
        """Return whether VM is suspended.
        """
        return self.status == self._model.STATUS_SUSPENDED

    @property
    def is_booting(self):
        """Return whether VM is booting.
        """
        return self.status == self._model.STATUS_BOOTING

    def select(self):
        """Select VM instance.

        Returns
        -------
        bool
            True - success.
        """
        self._model.name.click()
        return VMDetailsView(self.driver)

    def run(self):
        """Run VM.

        Returns
        -------
            True - success.
        """
        self._model.run_btn.click()
        return True

    def suspend(self):
        """Suspend VM.

        Returns
        -------
        bool
            True - success
        """
        self._model.suspend_btn.click()
        return True

    def shutdown(self):
        """Shutdown VM.

        Returns
        -------
            True - success
        """
        self._model.shutdown_btn.click()
        return True

    def restart(self):
        """Restart VM.

        Returns
        -------
        bool
            True - success.
        """
        self._model.restart_btn.click()
        return True


class VMDetailsView(page_base.PageObject):
    """Details view showing information about selected VM
    """
    _model = VMDetailsModel
    _label = 'Details'

    def init_validation(self):
        """Initial validation - check that VM instance is present.

        Returns
        -------
        bool
            True - successful validation.
        """
        self._model.name
        return True

    @property
    def name(self):
        """VM name.
        """
        return self._model.name.text

    @property
    def description(self):
        """VM description.
        """
        return self._model.description.text

    @property
    def os(self):
        """VM operating system.
        """
        return self._model.os.text

    @property
    def memory(self):
        """Memory defined for VM.
        """
        return self._model.memory.text

    @property
    def cores(self):
        """Number of cores defined for VM.
        """
        return self._model.cores.text

    @property
    def console_text(self):
        """VM console protocol.
        """
        return self._model.console.text

    def get_disk(self, name):
        return VDiskInstance(self.driver, name=name)

    def console_edit(self):
        """Edit console protocol of VM.

        Returns
        -------
           Console Options dialog.
        """
        self._model.console_edit.click()
        return vms_base.EditConsoleOptions(self.driver)

    # pylint: disable=E0102
    def console(self):
        """Invoke console for VM.

        Returns
        -------
            Console Options dialog
        """
        self._model.connect.click()
        time.sleep(3)  # Pause to save .vv file or auto-open it.


class VDiskInstance(page_base.DynamicPageObject):
    """Table row representing single Vdisk instance.
    """
    _timeout = 10
    _model = VDiskInstModel
    _label = 'Disk'

    def init_validation(self):
        """Initial validation.
        """
        self._model.alias.text

    @property
    def alias(self):
        """Vdisk alias.
        """
        return self._model.alias.text

    @property
    def size(self):
        """Vdisk size.
        """
        return self._model.size.text


class BasicTabCtrl(object):
    """Basic view tab controller. Handles actions like creating, editing and
    deleting a VM.

    Parameters
    ----------
    VM_ACTION_TIMEOUT
        Default timeout for VM actions like run_vm.
    """
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
        return VMInstance(self.driver, name=name)

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

    @deco.retry(8, exceptions=(excepts.WaitTimeoutError,))
    def _wait_for_vm_status(self, name, status_prop, timeout=None):
        """Wait until VM status property returns True.

        Parameters
        ----------
        name
            VM name
        status_prop : str
            Name of the status property, e.g. 'is_up'.
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
        status = getattr(vm, status_prop)
        if not status:
            msg = "%s - status is '%s'" % (vm, vm.status)
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
        marker = ('//div[starts-with(@id, '
                  '"MainTabBasicListView_vm")][contains(@id, "_name")]')
        vms = self.driver.find_elements(by.By.XPATH, marker)
        vms_names = [getattr(x, 'text') for x in vms]
        return set(vms_names)

    def get_vm_from_pool(self, pool_name):
        regex = vms_base.mk_pool_regex(pool_name)
        vms = self.get_vms_names()
        for vm_name in sorted(vms):
            if re.match(regex, vm_name):
                vm = VMInstance(self.driver, name=vm_name)
                if vm.is_up or vm.is_booting:
                    logger.info("Found active VM from pool %s: %s.",
                                pool_name,
                                vm_name)
                    return vm
        logger.info("Did not found active vm from pool: %s. Start a new one.",
                    pool_name)
        return self.start_vm_from_pool(pool_name)

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
                    vm = VMInstance(self.driver, name=vm_name)
                    if vm.is_up or vm.is_booting:
                        logger.info("Found a new active VM from pool %s: %s.",
                                    pool_name, vm_name)
                    return vm
