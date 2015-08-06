"""
rv_disconnect.py - Disconnects remote-viewer by kiling it.

"""
import logging
import os
from autotest.client.shared import error
from virttest import utils_spice


def run_rv_disconnect(test, params, env):
    """
    Test kills application. Application is given by name kill_app_name in
    params.
    It has to be defined if application is on guest or client with parameter
    kill_on_vms which should contain name(s) of vm(s) (separated with ',')

    :param test: KVM test object.
    :param params: Dictionary with the test parameters.
    :param env: Dictionary with test environment.
    """
    logging.debug("Killing remote-viewer on client")
    utils_spice.kill_app(params.get("client_vm"), params.get("rv_binary"), params, env)
