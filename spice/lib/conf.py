#!/usr/bin/env python

import logging

"""Default values used in spice tests."""

LOGIN_TIMEOUT = int("360")
"""SSH login timeout. Seconds."""

USERNAME = "root"
"""User name for ssh."""

PASSWORD = "123456"
"""Password for ssh."""

RV_BINARY = "/usr/bin/remote-viewer"
"""Path to remote viwer binary."""

TEST_TYPE_NEGATIVE = "negative"
"""Negative test type."""

SSL_TYPE_IMPLICIT = "implicit_hs"
"""SSL type - implicit host name."""

SSL_TYPE_EXPLICIT = "explicit_hs"
"""SSL type - explicit host name."""

SSL_TYPE_IMPLICIT_INVALID = "invalid_implicit_hs"
"""SSL type - invalid implicit host name."""

SSL_TYPE_EXPLICIT_INVALID = "invalid_explicit_hs"
"""SSL type - invalid explicit host name."""

PTRN_QEMU_SSL_ACCEPT_FAILED = "SSL_accept failed"
"""Pattern for qemu log - failed to accept SSL."""

AUDIO_REC_FILE = "./recorded.wav"
"""Recorded audio."""

class Params:
    """Class used to hold all known keys in cartesian configs known by Spice
    tests.  The default value is used if there is no provided one.

    Note
    ----
        As a rule, this parameters have value independent from VM.  Some keys
        can be specific for particular VM.

    Parameters
    ----------
    params : virttest.utils_params.Params
        Dictionary with the test parameters.
    """

    def __init__(self, params):
        self.login_timeout = LOGIN_TIMEOUT
        """Timeout for ssh."""
        self.spice_proxy = None
        """Proxy for HTTP connections."""
        self.ssltype = ""
        """.. todo:: provide info."""
        self.guest_vm = ""
        """Name for guest VM."""
        self.client_vm = ""
        """Name for client VM."""
        self.os_type = ""
        """VM OS. Know types: windows, linux."""
        self.rv_binary = RV_BINARY
        """.. todo:: provide info."""
        self.spice_secure_channels = ""
        """.. todo:: provide info."""
        self.test_type = ""
        """.. todo:: provide info."""
        self.spice_x509_prefix = ""
        """.. todo:: provide info."""
        self.spice_x509_cacert_file = ""
        """.. todo:: provide info."""
        self.rv_ld_library_path = ""
        """.. todo:: provide info."""
        self.display = ""
        """.. todo:: provide info."""
        self.disable_audio = "no"
        """.. todo:: provide info."""
        self.full_screen = ""
        """.. todo:: provide info."""
        self.spice_info = ""
        """.. todo:: provide info."""
        self.spice_password_send = ""
        """.. todo:: provide info."""
        self.qemu_password = ""
        """.. todo:: provide info."""
        self.gencerts = ""
        """.. todo:: provide info."""
        self.certdb = ""
        """.. todo:: provide info."""
        self.smartcard = ""
        """.. todo:: provide info."""
        self.rv_parameters_from = "cmd"
        """.. todo:: provide info."""
        self.rv_file = ""
        """.. todo:: provide info."""
        self.usb_redirection_add_device_vm2 = ""
        """.. todo:: provide info."""
        self.file_path = ""
        """.. todo:: provide info."""
        self.spice_client_host_subject = ""
        """.. todo:: provide info."""
        self.vms = ""
        """VM kvm names. Ex.: client guest."""
        self.spice_password = None
        """.. todo:: provide info."""
        for i in vars(self):
            if i in params:
                logging.info("Set %s to %s", i, params[i])
                setattr(self, i, params[i])