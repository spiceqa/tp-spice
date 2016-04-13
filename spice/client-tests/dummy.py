#!/usr/bin/env python

import logging
import time
import sys

def run(helper):
    for i in range(50):
        t = time.time()
        reply = helper.query_master(i, t)
        logging.info("Reply %s: %s", i, str(reply))
