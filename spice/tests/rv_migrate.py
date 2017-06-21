# #!/usr/bin/env python
#
# # This program is free software; you can redistribute it and/or modify
# # it under the terms of the GNU General Public License as published by
# # the Free Software Foundation; either version 2 of the License, or
# # (at your option) any later version.
# #
# # This program is distributed in the hope that it will be useful,
# # but WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# #
# # See LICENSE for more details.
#
# #TODO: We need a standalone migration that wouldn't rely on tp-qemu.
# #      Use migration from tp-qemu as a starting point, and make sure we will
# #      have an active connection
#
#
# import re
# import time
# import types
# import aexpect
# import logging
#
# from virttest import utils_misc
# from virttest import utils_test
# from avocado.core import exceptions
# from autotest.client.shared import error
#
# from spice.lib import stest
# from spice.lib import utils
# from spice.lib import act
#
#
# logger = logging.getLogger(__name__)
#
# # README
# # This test was never written.
# # It was compied from tp-qemu, and doesn't do anything useful.
# # Look at: qemu/tests/cfg/migrate.cfg
#
#
# def run(test, params, env):
#     """KVM migration test:
#
#     Info
#     ----
#
#         * Get a live VM and clone it.
#
#         * Verify that the source VM supports migration.  If it does, proceed
#         with the test.
#
#         * Send a migration command to the source VM and wait until it's
#         finished.  * Kill off the source VM.
#
#         * Log into the destination VM after the migration is finished.
#
#         * Compare the output of a reference command executed on the source
#         with the output of the same command on the destination machine.
#
#     Parameters
#     ----------
#     vt_test : avocado.core.plugins.vt.VirtTest
#         QEMU test object.
#     test_params : virttest.utils_params.Params
#         Dictionary with the test parameters.
#     env : virttest.utils_env.Env
#         Dictionary with test environment.
#
#     """
#
#     mig_speed = params.get("mig_speed", "1G")
#     vm.monitor.migrate_set_speed(mig_speed)
#     login_timeout = int(params.get("login_timeout", 360))
#     mig_timeout = float(params.get("mig_timeout", "3600"))
#     mig_protocol = params.get("migration_protocol", "tcp")
#     mig_cancel_delay = int(params.get("mig_cancel") == "yes") * 2
#     mig_exec_cmd_src = params.get("migration_exec_cmd_src")
#     mig_exec_cmd_dst = params.get("migration_exec_cmd_dst")
#     if mig_exec_cmd_src and "gzip" in mig_exec_cmd_src:
#         mig_exec_file = params.get("migration_exec_file", "/var/tmp/exec")
#         mig_exec_file += "-%s" % utils_misc.generate_random_string(8)
#         mig_exec_cmd_src = mig_exec_cmd_src % mig_exec_file
#         mig_exec_cmd_dst = mig_exec_cmd_dst % mig_exec_file
#     offline = params.get("offline", "no") == "yes"
#     check = params.get("vmstate_check", "no") == "yes"
#     living_guest_os = params.get("migration_living_guest", "yes") == "yes"
#     deamon_thread = None
#
#     vm = env.get_vm(params["main_vm"])
#     vm.verify_alive()
#
#     session = vm.wait_for_login(timeout=login_timeout)
#
#     # Start another session with the guest and make sure the background
#     # process is running
#     session2 = vm.wait_for_login(timeout=login_timeout)
#
#     try:  # where is except?
#         # run some functions before migrate start.
#         pre_migrate = get_functions(params.get("pre_migrate"), locals())
#         for func in pre_migrate:
#             func()
#
#         # Migrate the VM
#         ping_pong = params.get("ping_pong", 1)
#         for i in xrange(int(ping_pong)):
#             if i % 2 == 0:
#                 logging.info("Round %s ping..." % str(i / 2))
#             else:
#                 logging.info("Round %s pong..." % str(i / 2))
#             vm.migrate(mig_timeout, mig_protocol, mig_cancel_delay,
#                        offline, check,
#                        migration_exec_cmd_src=mig_exec_cmd_src,
#                        migration_exec_cmd_dst=mig_exec_cmd_dst, env=env)
#
#         # Set deamon thread action to stop after migrate
#         params["action"] = "stop"
#
#         # Make sure the background process is still running
#         error.context("Checking the background command in the guest "
#                       "post migration", logging.info)
#         session2.cmd(check_command, timeout=30)
