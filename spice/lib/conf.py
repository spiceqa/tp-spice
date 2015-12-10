#!/usr/bin/env python
"""
Default values used in spice tests
"""

USERNAME = "root"
""" User name for ssh. """

PASSWORD = "123456"
""" Password for ssh. """

RV_BINARY = "/usr/bin/remote-viewer"
""" Path to remote viwer binary. """

TEST_TYPE_NEGATIVE = "negative"
""" Negative test type. """

SSL_TYPE_IMPLICIT = "implicit_hs"
""" SSL type - implicit host name """

SSL_TYPE_EXPLICIT = "explicit_hs"
""" SSL type - explicit host name """

SSL_TYPE_IMPLICIT_INVALID = "invalid_implicit_hs"
""" SSL type - invalid implicit host name """

SSL_TYPE_EXPLICIT_INVALID = "invalid_explicit_hs"
""" SSL type - invalid explicit host name """

PTRN_QEMU_SSL_ACCEPT_FAILED = "SSL_accept failed"
""" Pattern for qemu log - failed to accept SSL """

AUDIO_REC_FILE = "./recorded.wav"
""" Recorded audio """
