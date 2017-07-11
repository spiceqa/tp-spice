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

from selenium.webdriver.common import by
from selenium.webdriver.support import ui

import page_base
import elements

logger = logging.getLogger(__name__)

TIMEOUT_MODAL_DIALOG = 30
TIMEOUT_MODAL_DIALOG_CLOSE = 60


class ModalDlgModel(page_base.PageModel):
    """Base page model for modal dialogs.
    """
    background_veil = elements.PageElement(by.By.CSS_SELECTOR,
                                           'div.gwt-PopupPanelGlass')


class OkCancelDlgModel(ModalDlgModel):
    """Base page model for dialog window containing 'OK' and 'Cancel' buttons.
    This is only a place holder class! Required page elements `ok_btn` and
    `cancel_btn` must be defined in all derived page models.
    """


class RemoveConfirmDlgModel(OkCancelDlgModel):
    """Page model for common removal confirmation dialog.
    """
    ok_btn = elements.Button(by.By.ID, 'RemoveConfirmationPopupView_OnRemove')
    cancel_btn = elements.Button(by.By.ID,
                                 'RemoveConfirmationPopupView_Cancel')


class ModalDlg(page_base.PageObject):
    """Base page object for all modal dialogs.
    """
    _timeout = TIMEOUT_MODAL_DIALOG
    _model = ModalDlgModel

    def wait_to_disappear(self, timeout=TIMEOUT_MODAL_DIALOG_CLOSE):
        """Wait `timeout` seconds until the dialog disappears.

        Parameters
        ----------
        timeout
            Timeout in seconds.
        """
        ui.WebDriverWait(self, timeout).until_not(
            lambda self: self._model.background_veil,
            "%s: timeout (%d seconds) expired. Dialog window is still present."
            % (self.__class__.__name__, timeout))


class OkCancelDlg(ModalDlg):
    """Abstract base page object for new-style dialog windows containing 'OK'
    and 'Cancel' buttons.  Note, that this page object implements only
    functionality for the OK & Cancel buttons. The button page elements must be
    defined in particular page model of the derived page object class.
    """
    _model = OkCancelDlgModel
    _label = 'OK/Cancel dialog'

    def init_validation(self):
        """Initial validation - check that 'Ok' and 'Cancel' buttons are
        present.

        Returns
        -------
        bool
            True - successful validation.
        """
        self._model.ok_btn
        self._model.cancel_btn
        return True

    def submit(self):
        """Submit dialog - just click on 'OK' button.

        Returns
        -------
        bool
            True.
        """
        # workaround for broken dialog submit via OK button click
        self._model.ok_btn.click()
        return True

    def submit_and_wait_to_disappear(self, timeout=TIMEOUT_MODAL_DIALOG_CLOSE):
        """Submit dialog and wait until all dialog windows disappear.  Caution:
        use only if you are sure, that after the dialog has been submitted, no
        other or new dialog windows are present!

        Parameters
        ----------
        timeout
            Number of seconds to wait until the window disappears.

        Returns
        -------
        bool
            True - success.
        """
        self.submit()
        self.wait_to_disappear(timeout)
        return True

    def cancel(self):
        """Cancel popup - click on 'Cancel' button.

        Returns
        -------
        bool
            True.
        """
        # workaround for broken dialog cancel via Cancel button click
        self._model.cancel_btn.click()
        return True


class RemoveConfirmDlg(OkCancelDlg):
    """New-style page object for removal confirmation dialogs.
    """
    _model = RemoveConfirmDlgModel
