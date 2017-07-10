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


"""Page objects for the Virtual Machines tab.
"""

import logging

from selenium.webdriver.common import by

from . import page_base
from . import dialogs
from . import elements
from . import excepts

logger = logging.getLogger(__name__)
TIMEOUT_TABLE_ROW = 10


# Models
class VMPopupModel(dialogs.OkCancelDlgModel):
    """ New/Edit Virtual Machine dialog.
    The code is also shared with `Edit Template` dialog. This is the reason
    why CSS locators '*[id$=...]' are used.
    """
    __tab_label_xpath = '//span[@class="gwt-InlineLabel"][text()="%s"]'

    ok_btn = elements.Button(by.By.CSS_SELECTOR, '*[id$=PopupView_OnSave]')
    cancel_btn = elements.Button(by.By.CSS_SELECTOR, '*[id$=PopupView_Cancel]')
    advanced_opts_btn = elements.Button(
        by.By.CSS_SELECTOR, '*[id$=PopupView_OnAdvanced]')

    general_tab = elements.PageElement(by.By.XPATH, __tab_label_xpath %
                                       'General')
    system_tab = elements.PageElement(by.By.XPATH, __tab_label_xpath %
                                      'System')
    init_run_tab = elements.PageElement(by.By.XPATH, __tab_label_xpath %
                                        'Initial Run')
    console_tab = elements.PageElement(by.By.XPATH, __tab_label_xpath %
                                       'Console')
    host_tab = elements.PageElement(by.By.XPATH, __tab_label_xpath % 'Host')
    high_avail_tab = elements.PageElement(
        by.By.XPATH, __tab_label_xpath % 'High Availability')
    res_alloc_tab = elements.PageElement(
        by.By.XPATH, __tab_label_xpath % 'Resource Allocation')
    boot_opts_tab = elements.PageElement(
        by.By.XPATH, __tab_label_xpath % 'Boot Options')
    custom_props_tab = elements.PageElement(
        by.By.XPATH, __tab_label_xpath % 'Custom Properties')

    cluster = elements.LabeledSelect(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_dataCenterWithCluster]')
    quota = elements.ComboBox(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_quota]')
    template = elements.ComboBox(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_templateWithVersion]')
    os_type = elements.Select(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_osType]')
    vm_type = elements.Select(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_vmType]')

    LABEL_ADVANCED_OPTS_SHOW = 'Show Advanced Options'
    LABEL_ADVANCED_OPTS_HIDE = 'Hide Advanced Options'


class VMPopupGeneralTabModel(page_base.PageModel):
    """ VM popup - 'General' side-tab. """
    name = elements.TextInput(by.By.CSS_SELECTOR, '*[id$=PopupWidget_name]')
    description = elements.TextInput(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_description]')
    is_stateless = elements.Checkbox(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_isStateless]')
    is_run_and_pause = elements.Checkbox(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_isRunAndPause]')
    is_delete_protected = elements.Checkbox(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_isDeleteProtected]')

    class VMNIC(page_base.DynamicPageModel):
        """ Model of the select element for assigned network of given NIC. """
        network = elements.DynamicSelect(
            by.By.CSS_SELECTOR, '*[id$=PopupWidget_networksEditor_%s]')

        @property
        def _instance_identifier(self):
            """ Return the NIC name,
            which is then used to identify the correct NIC.

            Returns: NIC name, e.g., nic1, nic2, etc.
            """
            return self._name


class VMPopupSystemTabModel(page_base.PageModel):
    """ VM popup - 'System' side-tab. """
    mem_size = elements.TextInput(by.By.CSS_SELECTOR,
                                  '*[id$=PopupWidget_memSize]')
    cpu_cores = elements.TextInput(by.By.CSS_SELECTOR,
                                   '*[id$=PopupWidget_totalCPUCores]')
    advanced_params_toggle = elements.PageElement(
        by.By.XPATH, '//div[contains(@class, "gwt-ToggleButton")]'
        '//span[. = "Advanced Parameters"]')
    cores_per_socket = elements.Select(by.By.CSS_SELECTOR,
                                       '*[id$=PopupWidget_coresPerSocket]')
    num_of_sockets = elements.Select(by.By.CSS_SELECTOR,
                                     '*[id$=PopupWidget_numOfSockets]')


class VMPopupInitRunTabModel(page_base.PageModel):
    """ VM popup - 'Initial Run' side-tab. """
    time_zone = elements.Select(by.By.CSS_SELECTOR,
                                '*[id$=PopupWidget_timeZone]')
    domain = elements.Select(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_domain]')


class VMPopupConsoleTabModel(page_base.PageModel):
    """ VM popup - 'Console' side-tab. """
    display_protocol = elements.Select(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_graphicsType]')
    vnc_kb_layout = elements.Select(by.By.CSS_SELECTOR,
                                    '*[id$=PopupWidget_vncKeyboardLayout]')
    usb_policy = elements.Select(by.By.CSS_SELECTOR,
                                 '*[id$=PopupWidget_usbPolicy]')
    num_of_monitors = elements.Select(by.By.CSS_SELECTOR,
                                      '*[id$=PopupWidget_numOfMonitors]')
    is_smartcard_enabled = elements.Checkbox(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_numOfMonitors]')

    advanced_params_toggle = elements.PageElement(
        by.By.XPATH,
        '//div[contains(@class, "gwt-ToggleButton")]'
        '//span[. = "Advanced Parameters"]')
    disable_strict_user_chk = elements.Checkbox(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_allowConsoleReconnect]')
    is_soundcard_enabled = elements.Checkbox(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_isSoundcardEnabled]')


class VMPopupHostTabModel(page_base.PageModel):
    """ VM popup - 'Host' side-tab. """
    any_host_in_cluster = elements.Select(
        by.By.XPATH, '(//input[@name="runVmOnHostGroup"])[1]')
    specific_host_radio = elements.Radio(
        by.By.XPATH, '(//input[@name="runVmOnHostGroup"])[2]')
    specific_host_sel = elements.Select(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_defaultHost]')
    migration_mode = elements.Select(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_migrationMode]')
    use_host_cpu = elements.Checkbox(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_hostCpu]')
    cpu_pinning = elements.TextInput(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_cpuPinning]')


class VMPopupHighAvailTabModel(page_base.PageModel):
    """ VM popup - 'High Availability' side-tab. """
    is_highly_available = elements.Checkbox(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_isHighlyAvailable]')
    migration_prio = elements.Select(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_priority]')
    watchdog_model = elements.Select(by.By.CSS_SELECTOR,
                                     '*[id$=PopupWidget_watchdogModel]')
    watchdog_action = elements.Select(by.By.CSS_SELECTOR,
                                      '*[id$=PopupWidget_watchdogAction]')
    PRIO_LOW = 'Low'
    PRIO_MEDIUM = 'Medium'
    PRIO_HIGH = 'High'


class VMPopupResAllocTabModel(page_base.PageModel):
    """ VM popup - 'Resource Allocation' tab. """
    phy_mem_guaranteed = elements.TextInput(
        by.By.CSS_SELECTOR,
        '*[id$=PopupWidget_minAllocatedMemory]')
    template_prov_thin = elements.Radio(by.By.CSS_SELECTOR,
                                        '*[id$=PopupWidget_provisioningThin]')
    template_prov_clone = elements.Radio(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_provisioningClone]')


class VMPopupBootOptsTabModel(page_base.PageModel):
    """ VM popup - 'Boot Options' tab. """
    boot_dev_1st = elements.Select(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_firstBootDevice]')
    boot_dev_2nd = elements.Select(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_secondBootDevice]')
    is_cd_attached = elements.Checkbox(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_cdAttached]')
    attach_cd = elements.Select(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_cdImage]')
    kernel_path = elements.TextInput(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_kernelPath]')
    initrd_path = elements.TextInput(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_initrdPath]')
    kernel_params = elements.TextInput(
        by.By.CSS_SELECTOR, '*[id$=PopupWidget_kernelParameters]')


class VMPopupCustPropsTabModel(page_base.PageModel):
    """ VM popup - 'Custom Properties' tab. """
    custom_props = elements.Select(by.By.CSS_SELECTOR,
                                   'div[id$=PopupWidget] select')


class NewTemplateDlgModel(dialogs.OkCancelDlgModel):
    """ New Template dialog. """
    name = elements.TextInput(by.By.ID, 'VmMakeTemplatePopupWidget_name')
    description = elements.TextInput(by.By.ID,
                                     'VmMakeTemplatePopupWidget_description')
    host_cluster = elements.ComboBox(
        by.By.ID, 'VmMakeTemplatePopupWidget_dataCenterWithCluster')
    quota = elements.Select(by.By.ID, 'VmMakeTemplatePopupWidget_quota')
    is_public = elements.Checkbox(by.By.ID,
                                  'VmMakeTemplatePopupWidget_isTemplatePublic')

    ok_btn = elements.Button(by.By.ID, 'VmMakeTemplatePopupView_OnNewTemplate')
    cancel_btn = elements.Button(by.By.ID, 'VmMakeTemplatePopupView_Cancel')


class NewTemplateDiskInstModel(page_base.DynamicPageModel):
    """ A single disk instance from Disks Allocation section. """
    _disk_names = elements.PageElement(by.By.CSS_SELECTOR,
                                       'input[id^="VmMakeTemplatePopupWidget_'
                                       'disksAllocation_disk"][id$=_diskName]',
                                       as_list=True)
    alias = elements.DynamicTextInput(
        by.By.ID, 'VmMakeTemplatePopupWidget_disksAllocation_disk%s_diskAlias')
    size = elements.DynamicTextInput(
        by.By.ID, 'VmMakeTemplatePopupWidget_disksAllocation_disk%s_diskSize')
    target_storage = elements.DynamicSelect(
        by.By.ID,
        'VmMakeTemplatePopupWidget_disksAllocation_disk%s_storageDomain')

    @property
    def _instance_identifier(self):
        """
        Identifier of a table row with template disk instance.
        Returns: disk row index based on disk alias
        Throws: ElementDoesNotExistError - instance does not exist
        """
        disk_names = [name.get_attribute('value') for name in self._disk_names]
        try:
            index = disk_names.index(self._name)
        except ValueError:
            raise excepts.ElementDoesNotExistError(self)
        return index


class CloneVmDlgModel(dialogs.OkCancelDlgModel):
    name = elements.TextInput(by.By.ID, 'CloneVmWidget_cloneName')
    ok_btn = elements.Button(by.By.ID, 'CloneVmPopupView_OnClone')
    cancel_btn = elements.Button(by.By.ID, 'CloneVmPopupView_Cancel')


class GuestAgentIsNotResponsiveDlgModel(dialogs.OkCancelDlgModel):
    cancel_btn = elements.Button(by.By.ID, 'DefaultConfirmationPopupView_'
                                 'SpiceWithoutAgentCancel')
    ok_btn = elements.Button(by.By.ID, 'DefaultConfirmationPopupView_'
                             'SpiceWithoutAgentOK')


class GuestAgentIsNotResponsiveDlg(dialogs.OkCancelDlg):
    _model = GuestAgentIsNotResponsiveDlgModel
    _label = 'Guest Agent is not responsive'

    @classmethod
    def ok_ignore(cls, drv):
        try:
            no_agent_dialog = cls(drv, timeout=0.1)
            no_agent_dialog._model.ok_btn.click()
        except excepts.InitPageValidationError:
            logger.info("Guest Agent dialog does not exist.")


class VMPopup(dialogs.OkCancelDlg):
    """Page object of the New/Edit VM popup.
    Provides logic for filling out all form fields.
    """
    _model = VMPopupModel
    _label = 'New/Edit Virtual Machine dialog'

    def init_validation(self):
        """ Initial validation - check that VM dialog is present. """
        self._model.general_tab

    def _go_to_general_tab(self):
        self._model.general_tab.click()
        return VMPopupGeneralTab(self.driver)

    def _go_to_system_tab(self):
        self._model.system_tab.click()
        return VMPopupSystemTab(self.driver)

    def _go_to_init_run_tab(self):
        self._model.init_run_tab.click()
        return VMPopupInitRunTab(self.driver)

    def _go_to_console_tab(self):
        self._model.console_tab.click()
        return VMPopupConsoleTab(self.driver)

    def _go_to_host_tab(self):
        self._model.host_tab.click()
        return VMPopupHostTab(self.driver)

    def _go_to_high_avail_tab(self):
        self._model.high_avail_tab.click()
        return VMPopupHighAvailTab(self.driver)

    def _go_to_res_alloc_tab(self):
        self._model.res_alloc_tab.click()
        return VMPopupResAllocTab(self.driver)

    def _go_to_boot_opts_tab(self):
        self._model.boot_opts_tab.click()
        return VMPopupBootOptsTab(self.driver)

    def _go_to_cust_props_tab(self):
        self._model.custom_props_tab.click()
        return VMPopupCustPropsTab(self.driver)

    def _fill_values(self, cluster=None, quota=None, template=None,
                     os_type=None, vm_type=None):
        """ Fill out only the common form fields on the main VM popup.

        Parameters:
          - cluster (str): cluster name
          - quota (str): quota (if applicable)
          - template (str): template
          - os_type (str): guest OS type
          - vm_type (str): VM type (Optimized for)
        """
        self._model.cluster = cluster
        self._model.quota = quota
        self._model.template = template
        self._model.os_type = os_type
        self._model.vm_type = vm_type

    def show_advanced_options(self):
        """ Click on 'Show Advanced Options' button. """
        if (self._model.advanced_opts_btn.text ==
                self._model.LABEL_ADVANCED_OPTS_SHOW):
            self._model.advanced_opts_btn.click()
            logger.debug("VM advanced options expanded.")

    def hide_advanced_options(self):
        """ Click on 'Hide Advanced Options' button. """
        if (self._model.advanced_opts_btn.text ==
                self._model.LABEL_ADVANCED_OPTS_HIDE):
            self._model.advanced_opts_btn.click()
            logger.debug("VM advanced options collapsed.")

    def fill_values(
            self, name=None, description=None,
            is_stateless=None, is_run_and_pause=None, is_delete_protected=None,
            nic_networks=None, cluster=None, quota=None, template=None,
            os_type=None, vm_type=None, memory_size=None, cpu_cores=None,
            cores_per_socket=None, num_of_sockets=None, time_zone=None,
            domain=None, display_protocol=None, vnc_kb_layout=None,
            usb_policy=None, num_of_monitors=None, is_smartcard_enabled=None,
            disable_strict_user_chk=None, is_soundcard_enabled=None,
            run_on_host=None, migration_mode=None, use_host_cpu=None,
            cpu_pinning=None, is_highly_available=None,
            migration_prio=None, watchdog_model=None, watchdog_action=None,
            phy_mem_guaranteed=None, template_prov=None, boot_dev_1st=None,
            boot_dev_2nd=None, attach_cd=None, kernel_path=None,
            initrd_path=None, kernel_params=None, custom_props=None):
        """ Fill out given form fields on all relevant side-tabs.

        Parameters:
          - see parameters of related `VMPopup*Tab.fill_values()` methods
        """
        self.show_advanced_options()

        self._fill_values(cluster=cluster, quota=quota, template=template,
                          os_type=os_type, vm_type=vm_type)
        # General tab
        if not (name is description is is_stateless is is_run_and_pause is
                is_delete_protected is nic_networks is None):
            self._go_to_general_tab().fill_values(
                name=name, description=description, is_stateless=is_stateless,
                is_run_and_pause=is_run_and_pause,
                is_delete_protected=is_delete_protected,
                nic_networks=nic_networks)
        # System tab
        if not (memory_size is cpu_cores is cores_per_socket is
                num_of_sockets is None):
            self._go_to_system_tab().fill_values(
                memory_size=memory_size,
                cpu_cores=cpu_cores, cores_per_socket=cores_per_socket,
                num_of_sockets=num_of_sockets)
        # Initial Run tab
        if not (time_zone is domain is None):
            self._go_to_init_run_tab().fill_values(time_zone=time_zone,
                                                   domain=domain)
        # Console tab
        if not (display_protocol is vnc_kb_layout is usb_policy is
                num_of_monitors is is_smartcard_enabled is
                disable_strict_user_chk is is_soundcard_enabled is None):
            self._go_to_console_tab().fill_values(
                display_protocol=display_protocol,
                vnc_kb_layout=vnc_kb_layout, usb_policy=usb_policy,
                num_of_monitors=num_of_monitors,
                is_smartcard_enabled=is_smartcard_enabled,
                disable_strict_user_chk=disable_strict_user_chk,
                is_soundcard_enabled=is_soundcard_enabled)
        # Host tab
        if not (run_on_host is migration_mode is use_host_cpu is
                cpu_pinning is None):
            self._go_to_host_tab().fill_values(
                run_on_host=run_on_host, migration_mode=migration_mode,
                use_host_cpu=use_host_cpu, cpu_pinning=cpu_pinning)
    # HA tab
        if not (is_highly_available is migration_prio is watchdog_model is
                watchdog_action is None):
            self._go_to_high_avail_tab().fill_values(
                is_highly_available=is_highly_available,
                migration_prio=migration_prio,
                watchdog_model=watchdog_model,
                watchdog_action=watchdog_action)
        # Resource Allocation tab
        if not (phy_mem_guaranteed is template_prov is None):
            self._go_to_res_alloc_tab().fill_values(
                phy_mem_guaranteed=phy_mem_guaranteed,
                template_prov=template_prov)
        # Boot Options tab
        if not (boot_dev_1st is boot_dev_2nd is attach_cd is kernel_path is
                initrd_path is kernel_params is None):
            self._go_to_boot_opts_tab().fill_values(
                boot_dev_1st=boot_dev_1st, boot_dev_2nd=boot_dev_2nd,
                attach_cd=attach_cd, kernel_path=kernel_path,
                initrd_path=initrd_path, kernel_params=kernel_params)
        # Custom Properties tab
        if custom_props is not None:
            self._go_to_cust_props_tab().fill_values(custom_props)


class VMPopupGeneralTab(page_base.PageObject):
    """ VM popup - 'General' tab. """
    _model = VMPopupGeneralTabModel
    _label = 'VM popup - General side-tab'

    class VMNIC(page_base.DynamicPageObject):
        """ VM NIC a logical network can be assigned to. """
        _model = VMPopupGeneralTabModel.VMNIC
        _label = 'VM NIC'

        def assign_network(self, network):
            """ Select given logical `network` to the NIC.

            Parameters:
              - network (str): logical network to be assigned
            """
            self._model.network = network

        def init_validation(self):
            raise NotImplementedError

    def init_validation(self):
        """ Initial validation - check for some element from the side-tab. """
        self._model.name

    def fill_values(self, name=None, description=None, is_stateless=None,
                    is_run_and_pause=None, is_delete_protected=None,
                    nic_networks=None):
        """ Fill out given form fields.

        Parameters:
          - name (str): VM name
          - description (str): VM description
          - is_stateless (bool): is VM stateless
          - is_run_and_pause (bool): start VM in pause mode
          - is_delete_protected (bool): enable/disable delete protection
          - nic_networks (list): network(s) assigned to NIC(s);
             format: ['nic1:rhevm-prod', 'nic2:rhevm-test', ...]
        """
        self._model.name = name
        self._model.description = description
        self._model.is_stateless = is_stateless
        self._model.is_run_and_pause = is_run_and_pause
        self._model.is_delete_protected = is_delete_protected
        nic_networks = nic_networks or []
        for nic, net in (item.split(':') for item in nic_networks):
            nic = self.VMNIC(self.driver, name=nic)
            nic.assign_network(net)


class VMPopupSystemTab(page_base.PageObject):
    """ VM popup - 'System' tab. """
    _model = VMPopupSystemTabModel
    _label = 'VM popup - System side-tab'

    def init_validation(self):
        """ Initial validation - check for some element from the side-tab. """
        self._model.mem_size

    def fill_values(self, memory_size=None, cpu_cores=None,
                    cores_per_socket=None, num_of_sockets=None):
        """ Fill out given form fields.

        Parameters:
          - memory_size (str): memory size (1G, 1 GB, 1024 MB, ...)
          - cpu_cores (int): total virtual CPU cores
          - cores_per_socket (int): cores per socket
          - num_of_sockets (int): number of sockets
        """
        # memory size input must be set twice, otherwise UI puts '[N/A]'
        # text before the value (reproducible only in automation)
        self._model.mem_size = memory_size
        self._model.mem_size = memory_size
        self._model.cpu_cores = cpu_cores
        if not (num_of_sockets is cores_per_socket is None):
            self._model.advanced_params_toggle.click()
            self._model.num_of_sockets = num_of_sockets
            self._model.cores_per_socket = cores_per_socket


class VMPopupInitRunTab(page_base.PageObject):
    """ VM popup - 'Initial Run' side-tab. """
    _model = VMPopupInitRunTabModel
    _label = 'VM popup - Initial Run side-tab'

    def init_validation(self):
        """ Initial validation - check for some element from the side-tab. """
        self._model.time_zone

    def fill_values(self, time_zone=None, domain=None):
        """ Fill out given form fields.

        Parameters:
          - time_zone (str): time zone
          - domain (str): Windows domain
        """
        self._model.time_zone = time_zone
        self._model.domain = domain


class VMPopupConsoleTab(page_base.PageObject):
    """ VM popup - 'Console' tab. """
    _model = VMPopupConsoleTabModel
    _label = 'VM popup - Console side-tab'

    def init_validation(self):
        """ Initial validation - check for some element from the side-tab. """
        self._model.display_protocol

    def fill_values(self, display_protocol=None, vnc_kb_layout=None,
                    usb_policy=None, num_of_monitors=None,
                    is_smartcard_enabled=None, disable_strict_user_chk=None,
                    is_soundcard_enabled=None):
        """ Fill out given form fields.

        Parameters:
          - display_protocol (str): display protocol
          - vnc_kb_layout (str): VNC keyboard layout (VNC only)
          - usb_policy (str): USB support
          - num_of_monitors (int): number of monitors
          - is_smartcard_enabled (bool): is smartcard enabled
          - disable_strict_user_chk (bool): disable strict user checking
          - is_soundcard_enabled (bool): is soundcard enabled
        """
        self._model.display_protocol = display_protocol
        self._model.vnc_kb_layout = vnc_kb_layout
        self._model.usb_policy = usb_policy
        self._model.num_of_monitors = num_of_monitors
        self._model.is_smartcard_enabled = is_smartcard_enabled
        if disable_strict_user_chk is not None:
            self._model.advanced_params_toggle.click()
            self._model.disable_strict_user_chk = disable_strict_user_chk
        self._model.is_soundcard_enabled = is_soundcard_enabled


class VMPopupHostTab(page_base.PageObject):
    """ VM popup - 'Host' tab. """
    _model = VMPopupHostTabModel
    _label = 'VM popup - Host side-tab'

    def init_validation(self):
        """ Initial validation - check for some element from the side-tab. """
        self._model.any_host_in_cluster

    def fill_values(self, run_on_host=None, migration_mode=None,
                    use_host_cpu=None, cpu_pinning=None):
        """ Fill out given form fields.

        Parameters:
          - run_on_host (str): run on host
            options: ANY - any host in cluster; or specific host name
          - migration_mode (str): migration option
          - use_host_cpu (bool): use host CPU
          - cpu_pinning (str): CPU pinning topology
        """
        if run_on_host is not None:
            if run_on_host == 'ANY':
                self._model.any_host_in_cluster.click()
            else:
                self._model.specific_host_radio.click()
                self._model.specific_host_sel = run_on_host
        self._model.migration_mode = migration_mode
        self._model.use_host_cpu = use_host_cpu
        self._model.cpu_pinning = cpu_pinning


class VMPopupHighAvailTab(page_base.PageObject):
    """ VM popup - 'High Availability' tab. """
    _model = VMPopupHighAvailTabModel
    _label = 'VM popup - High Availability tab'

    def init_validation(self):
        """ Initial validation - check for some element from the side-tab. """
        self._model.is_highly_available

    def select_migration_prio_low(self):
        """ Select low migration priority. """
        self._model.migration_prio = self._model.PRIO_LOW

    def select_migration_prio_medium(self):
        """ Select medium migration priority. """
        self._model.migration_prio = self._model.PRIO_MEDIUM

    def select_migration_prio_high(self):
        """ Select high migration priority. """
        self._model.migration_prio = self._model.PRIO_HIGH

    def fill_values(self, is_highly_available=None, migration_prio=None,
                    watchdog_model=None, watchdog_action=None):
        """ Fill out given form fields.

        Parameters:
          - is_highly_available (bool): is VM highly available
          - migration_prio (str): migration priority; options: LOW|MEDIUM|HIGH
          - watchdog_model (str): watchdog model
          - watchdog_action (str): watchdog action
        Throws: WrongParameterError - wrong parameter was entered
        """
        self._model.is_highly_available = is_highly_available
        if migration_prio is not None:
            migration_prio_action = {
                'LOW': self.select_migration_prio_low,
                'MEDIUM': self.select_migration_prio_medium,
                'HIGH': self.select_migration_prio_high
            }
            try:
                migration_prio_action[migration_prio]()
            except KeyError:
                raise excepts.errors.WrongParameterError(migration_prio)
        self._model.watchdog_model = watchdog_model
        self._model.watchdog_action = watchdog_action


class VMPopupResAllocTab(page_base.PageObject):
    """ VM popup - 'Resource Allocation' tab. """
    _model = VMPopupResAllocTabModel
    _label = 'VM popup -  Resource Allocation tab'

    def init_validation(self):
        """ Initial validation - check for some element from the side-tab. """
        self._model.phy_mem_guaranteed

    def set_thin_template_provisioning(self):
        """ Select thin template provisioning. """
        self._model.template_prov_thin.clik()

    def set_clone_template_provisioning(self):
        """ Select clone template provisioning. """
        self._model.template_prov_clone.clik()

    def fill_values(self, phy_mem_guaranteed=None, template_prov=None):
        """ Fill out given form fields.

        Parameters:
          - phy_mem_guaranteed (str): physical memory guaranteed
          - template_prov (str): template provisioning; options: THIN|CLONE
        """
        # memory guaranteed input must be set twice, otherwise UI puts '[N/A]'
        # text before the value (reproducible only in automation)
        self._model.phy_mem_guaranteed = phy_mem_guaranteed
        self._model.phy_mem_guaranteed = phy_mem_guaranteed
        if template_prov is not None:
            template_prov_action = {
                'THIN': self.set_thin_template_provisioning,
                'CLONE': self.set_clone_template_provisioning
            }
            try:
                template_prov_action[template_prov]()
            except KeyError:
                raise excepts.errors.WrongParameterError(template_prov)


class VMPopupBootOptsTab(page_base.PageObject):
    """ VM popup - 'Boot Options' tab. """
    _model = VMPopupBootOptsTabModel
    _label = 'VM popup -  Boot Options tab'

    def init_validation(self):
        """ Initial validation - check for some element from the side-tab. """
        self._model.boot_dev_1st

    def fill_values(self, boot_dev_1st=None, boot_dev_2nd=None,
                    attach_cd=None, kernel_path=None, initrd_path=None,
                    kernel_params=None):
        """ Fill out given form fields.

        Parameters:
          - boot_dev_1st (str): first boot device
          - boot_dev_2nd (str): second boot device
          - attach_cd (str): attach CD
              options: False or empty string - disable; or CD image name
          - kernel_path (str): kernel path
          - initrd_path (str): initrd path
          - kernel_params (str): kernel parameters
        """
        self._model.boot_dev_1st = boot_dev_1st
        self._model.boot_dev_2nd = boot_dev_2nd
        if attach_cd is not None:
            if attach_cd:
                self._model.is_cd_attached = True
                self._model.attach_cd = attach_cd
            else:
                self._model.is_cd_attached = False
        self._model.kernel_path = kernel_path
        self._model.initrd_path = initrd_path
        self._model.kernel_params = kernel_params


class VMPopupCustPropsTab(page_base.PageObject):
    """ VM popup - 'Custom Properties' tab. """
    _model = VMPopupCustPropsTabModel
    _label = 'VM popup -  Custom Properties tab'

    def init_validation(self):
        """ Initial validation - check for some element from the side-tab. """
        self._model.custom_props

    def fill_values(self, custom_props=None):
        """ Fill out given form fields.

        Parameters:
          - custom_props (str): custom property
        """
        self._model.custom_props = custom_props


class NewTemplateDlg(dialogs.OkCancelDlg):
    """ New Template dialog. """
    _model = NewTemplateDlgModel
    _label = 'New Template dialog'

    class NewTemplateDiskInst(page_base.DynamicPageObject):
        """ New template disk instance """
        _model = NewTemplateDiskInstModel
        _timeout = TIMEOUT_TABLE_ROW
        _label = "New template disk instance"

        def init_validation(self):
            """ Page object initial validation. """
            self._model.alias

        def fill_values(self, alias=None, target_storage=None):
            """ Set values for template disk. """
            self._model.alias = alias
            if target_storage is not None:
                self._model.target_storage.select_by_value_starting_with(
                    target_storage)
            return self

    def fill_values(self, name, description=None, cluster=None, quota=None,
                    is_public=None):
        """ Fill out fields for new VM template (except Disks Allocation part).
        Parameters:
          - name (str): template name
          - description (str): template desciption
          - cluster (str): Host Cluster
          - quota (str): quota
          - is_public (bool): Allow all users to access this Template
        Returns: self
        """
        self._model.name = name
        self._model.description = description
        self._model.host_cluster = cluster
        self._model.quota = quota
        self._model.is_public = is_public
        return self

    def fill_values_disk_alloc(self, alias, new_alias=None,
                               target_storage=None):
        """ Fill out values of single disk in Disks Allocation section.
        Parameters:
          - alias (str): disk alias
          - new_alias (str): new disk alias
          - target_storage (str): target storage
        Returns: self
        """
        self.NewTemplateDiskInst(self.driver, name=alias).fill_values(
            alias=new_alias, target_storage=target_storage)
        return self


class CloneVmDlg(dialogs.OkCancelDlg):
    _model = CloneVmDlgModel
    _label = 'Clone VM dialog'

    def fill_name(self, name):
        self._model.name = name


class EditConsoleOptionsModel(dialogs.OkCancelDlgModel):
    """ Edit console options dialog """
    spice_console = elements.Radio(by.By.ID,
                                   "ConsolePopupView_spiceRadioButton")
    vnc_console = elements.Radio(by.By.ID, "ConsolePopupView_vncRadioButton")
    rd_console = elements.Radio(by.By.ID,
                                "ConsolePopupView_remoteDesktopRadioButton")
    auto_console_inv = elements.Radio(
        by.By.ID, "ConsolePopupView_spiceAutoImplRadioButton")
    native_client_console_inv = elements.Radio(
        by.By.ID, "ConsolePopupView_spiceNativeImplRadioButton")
    browser_plugin_console_inv = elements.Radio(
        by.By.ID, "ConsolePopupView_spicePluginImplRadioButton")
    html5_console_inv = elements.Radio(
        by.By.ID, "ConsolePopupView_spiceHtml5ImplRadioButton")
    remap_ctrl_alt_del = elements.Checkbox(
        by.By.ID, "ConsolePopupView_remapCtrlAltDeleteSpice")
    enable_usb_auto_share = elements.Checkbox(
        by.By.ID, "ConsolePopupView_enableUsbAutoshare")
    open_in_fullscreen = elements.Checkbox(
        by.By.ID, "ConsolePopupView_openInFullScreen")
    enable_spice_proxy = elements.Checkbox(
        by.By.ID, "ConsolePopupView_enableSpiceProxy")
    disable_smartcard = elements.Checkbox(
        by.By.ID, "ConsolePopupView_disableSmartcard")
    enable_wan = elements.Checkbox(
        by.By.ID, "ConsolePopupView_wanEnabled")
    ok_btn = elements.Button(by.By.ID, "ConsolePopupView_OnEditConsoleSave")
    cancel_btn = elements.Button(by.By.ID, "ConsolePopupView_Cancel")


class EditConsoleOptions(dialogs.OkCancelDlg):
    """ Console options dialog """
    _label = "Edit console options dialog"
    _model = EditConsoleOptionsModel

    def init_validation(self):
        """ Initial validation if console options dialog is present """
        self._model.spice_console

    def _set_spice_console(self):
        self._model.spice_console = True

    def _set_vnc_console(self):
        self._model.vnc_console = True

    def _set_rd_console(self):
        self._model.rd_console = True

    def _set_auto_invocation(self):
        self._model.auto_console_inv = True

    def _set_native_invocation(self):
        self._model.native_client_console_inv = True

    def _set_browser_invocation(self):
        self._model.browser_plugin_console_inv = True

    def _set_html5_invocation(self):
        self._model.html5_console_inv = True

    def fill_values(self, console=None, console_inv=None,
                    remap_ctrl_alt_del=None, enable_usb=None,
                    open_in_fullscreen=None, spice_proxy=None,
                    enable_wan=None, disable_smartcard=None):
        """Fill console options dialog values.

        Parameters
        ----------
        console : str
            SPICE/VNC/RD protocol.
        console_inv : str
            Auto/Native/Browser/HTML5 console invocation.
        remap_ctrl_alt_del : bool
            Should ctrl+alt+del be remapped?
        enable_usb : bool
            Enable usb auto-share?
        open_in_fullscreen : bool
            Open console in fullscreen?
        enable_spice_proxy : bool
            Enable spice proxy?
        enable_wan : bool
            Enable WAN?
        disable_smartcard : bool
            Disable smartcard?
        """
        if console is not None:
            console_protocol = {'SPICE': self._set_spice_console,
                                'VNC': self._set_vnc_console,
                                'RD': self._set_rd_console}
            try:
                console_protocol[console]()
            except KeyError as ex:
                raise excepts.UserActionError(
                    "Unknown console protocol: %s. Accepted values: %s"
                    % (ex, console_protocol.keys()))

        if console_inv is not None:
            console_inv_option = {'Auto': self._set_auto_invocation,
                                  'Native': self._set_native_invocation,
                                  'Browser': self._set_browser_invocation,
                                  'HTML5': self._set_html5_invocation}
            try:
                console_inv_option[console_inv]()
            except KeyError as ex:
                raise excepts.UserActionError(
                    "Unknown console invocation: %s. Accepted values: %s"
                    % (ex, console_inv_option.keys()))

        if remap_ctrl_alt_del is not None:
            self._model.remap_ctrl_alt_del = remap_ctrl_alt_del
        if enable_usb is not None:
            self._model.enable_usb_auto_share = enable_usb
        if open_in_fullscreen is not None:
            self._model.open_in_fullscreen = open_in_fullscreen
        if spice_proxy is not None:
            self._model.enable_spice_proxy = spice_proxy
        if disable_smartcard is not None:
            self._model.enable_spice_proxy = disable_smartcard
        if enable_wan is not None:
            self._model.enable_spice_proxy = enable_wan

    @property
    def fullscreen_is_checked(self):
        """Return fullscreen.
        """
        return self._model.open_in_fullscreen.is_checked
        #console._model.open_in_fullscreen.check
        #console._model.open_in_fullscreen.is_checked
        #console._model.open_in_fullscreen.do_check
        #console._model.open_in_fullscreen.uncheck

    @property
    def spice_is_selected(self):
        return self._model.spice_console.is_selected()

    def select_rdp(self):
        self._set_rd_console()

    def select_vnc(self):
        self._set_vnc_console()

    def select_spice(self):
        self._set_spice_console()

    def select_inv_auto(self):
        self._set_auto_invocation()

    def select_inv_native(self):
        self._set_native_invocation()

    def select_inv_html5(self):
        self._set_html5_invocation()

    def set_ctrl_alt_del(self, val):
        self._model.remap_ctrl_alt_del = val

    def set_usb_auto_share(self, val):
        self._model.enable_usb_auto_share = val

    def set_open_in_fullscreen(self, val):
        self._model.open_in_fullscreen = val

    def set_spice_proxy(self, val):
        self._model.enable_spice_proxy = val

    def set_disable_smartcard(self, val):
        self._model.disable_smartcard = val

    def set_enable_wan(self, val):
        self._model.enable_wan = val


def mk_pool_regex(pool_name):
    if '?' in pool_name:
        regex = pool_name.replace('?', r'\d')  # Matches any decimal digit.
    else:
        regex = pool_name + r'\d'
    regex = regex + '$'
    logger.info("Use pool_name: %s, use regex: %s.", pool_name, regex)
    return regex
