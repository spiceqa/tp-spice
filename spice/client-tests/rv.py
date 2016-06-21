#!/usr/bin/python

import platform
import logging

logger = logging.getLogger(__name__)

distr_ver = platform.dist()[1]

if '7.' in distr_ver:
    logger.info("Import classes for dogtail for RHEL7.")
    from rv7 import *
elif '6.' in distr_ver:
    logger.info("Import classes for dogtail for RHEL6.")
    from rv6 import *
else:
    raise Exception("Not implemented for %s." % distr_ver)
