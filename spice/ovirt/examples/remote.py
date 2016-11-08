#!/usr/bin/python
from selenium import webdriver
command_executor='http://spiceqe.brq.redhat.com:5001/wd/hub'
driver = webdriver.Remote(command_executor=command_executor,
                          desired_capabilities={'browserName': 'firefox'})
