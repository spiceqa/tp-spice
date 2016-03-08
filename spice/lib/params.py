#!/usr/bin/env python

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

"""Holds knows parameters for all tests.
"""


class Params(object):
    """Class used to hold all known keys in cartesian configs known by Spice
    tests. The default value is used if there is no provided one.

    Note
    ----
        As a rule, this parameters have value independent from VM.  Some keys
        can be specific for particular VM.
    """
    remote_user = "root"
    """User for remote ssh session."""
    password = "123456"
    """User for remote ssh session."""
    login_timeout = "360"
    """SSH login timeout. Seconds."""
    spice_proxy = ""
    """Proxy for HTTP connections. Format is IP:PORT"""
    ssltype = ""
    """.. todo:: provide info."""
    guest_vm = ""
    """Name for guest VM."""
    client_vm = ""
    """Name for client VM."""
    os_type = ""
    """VM OS. Know types: windows, linux."""
    rv_binary = "/usr/bin/remote-viewer"
    """.. todo:: provide info."""
    spice_secure_channels = ""
    """.. todo:: provide info."""
    test_type = ""
    """.. todo:: provide info."""
    spice_x509_prefix = ""
    """.. todo:: provide info."""
    spice_x509_cacert_file = ""
    """.. todo:: provide info."""
    rv_ld_library_path = ""
    """.. todo:: provide info."""
    display = ""
    """RV protocol: vnc, spice. Currently supported only are: spice."""
    full_screen = ""
    """.. todo:: provide info."""
    spice_info = ""
    """.. todo:: provide info."""
    spice_password_send = ""
    """.. todo:: provide info."""
    qemu_password = ""
    """.. todo:: provide info."""
    gencerts = ""
    """.. todo:: provide info
    --spice-smartcard-certificates parameter."""
    certdb = ""
    """.. Certificate database for remote-viewer. /etc/pki/nssdb/
    --spice-smartcard-db parameter."""
    smartcard = ""
    """.. todo:: provide info. Yes/No"""
    rv_parameters_from = "cmd"
    """Could be: file, menu, cmd"""
    rv_file = ""
    """.. todo:: provide info."""
    usb_redirection_add_device_vm2 = ""
    """.. todo:: provide info."""
    file_path = ""
    """USB mount path."""
    spice_client_host_subject = ""
    """.. todo:: provide info."""
    vms = ""
    """VM kvm names. Ex.: client guest."""
    spice_password = None
    """.. todo:: provide info."""
    # : obsolete in favour sox
    audio_src = None
    """rv_audio test. Path to your audio file. Recomendation: generate
    square/sine wave file. File can be played on client - testing
    recording.  File can be played an guest - testing playback."""
    audio_tgt = None
    """.. todo:: provide info."""
    audio_rec = None
    """rv_audio test. Record to this temporary file."""
    audio_time = int("200")
    """rv_audio test. arecord capture time."""
    config_test = "no"
    """Could be: "no", "migration"."""
    rv_record = ""
    """Flag to test playback or record. yes - test recording. Other -
    playback."""
    disable_audio = "no"
    """rv_audio test. Could be: yes, no."""
    rv_audio_threshold = 25000
    """rv_audio test. """
    repeat_video = "No"
    """rv_video test. Repeat video in totem. Yes/No."""
    fullscreen = "No"
    """rv_video test. Run totem in fullscreen. Yes/No."""
    destination_video_file_path = "/tmp/test.ogv"
    """rv_video test. Video file for totem."""
    source_video_file = "video_sample_test.ogv"
    """rv_video test. Source video file for totem."""
    fedoraurl = ""
    """Used in rv_gui tests."""
    wmctrl_64rpm = ""
    """Used in rv_gui tests."""
    wmctrl_32rpm = ""
    """Used in rv_gui tests."""
    dogtail_rpm = ""
    """Used in rv_gui tests."""
    spice_password_send = ""
    """rv_ssn Used in RV connection setup."""
    qemu_password = ""
    """rv_ssn Used in RV connection setup."""
    rv_ld_library_path = ""
    """rv_ssn Used in RV connection setup. Could be set, for example to:
    /usr/local/lib. LD_LIBRARY_PATH= var"""
    shell_escape_char = ""
    """rv_ssn Could be: ^ or /"""
    usb_redirection_add_device = ""
    """rv_ssn Yes/No"""
    pnputil = ""
    """utils"""
    must_fail = "No"
    """Flag to show that the test should fail."""
    pause_on_end = "No"
    """Do not shutdown VMs for some time."""
    pause_on_fail = "No"
    """Do not shutdown VMs for some time if test has been failed."""

# Complete list is defined at avocado-vt/virttest/qemu_vm.py spice_keys=, make
# duplication.
KVM_SPICE_KNOWN_PARAMS = [
    "spice_port",
    "spice_password",
    "spice_addr",
    "spice_ssl",
    "spice_tls_port",
    "spice_tls_ciphers",
    "spice_gen_x509",
    "spice_x509_dir",
    "spice_x509_prefix",
    "spice_x509_key_file",
    "spice_x509_cacert_file",
    "spice_x509_key_password",
    "spice_x509_secure",
    "spice_x509_cacert_subj",
    "spice_x509_server_subj",
    "spice_secure_channels",
    "spice_image_compression",
    "spice_jpeg_wan_compression",
    "spice_zlib_glz_wan_compression",
    "spice_streaming_video",
    "spice_agent_mouse",
    "spice_playback_compression",
    "spice_ipv4",
    "spice_ipv6",
    "spice_x509_cert_file",
    "disable_copy_paste",
    "spice_seamless_migration",
    "listening_addr"]
