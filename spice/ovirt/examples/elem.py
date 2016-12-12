#!/usr/bin/python

"""Example: manual checking for elements on web-page.

USE
---
    execfile("elem.py")

"""
from selenium import webdriver
from selenium.webdriver.common.by import By
driver = webdriver.Firefox()

# Go to admin and select running VM.


def example():
    """Address the same element in different ways.
    """
    a = driver.find_element(
        By.XPATH, '//div[starts-with(@id, "MainTabVirtualMachineView_table_ConsoleConnectCommand")]')
    b = driver.find_element(
        By.XPATH, '//div[starts-with(@id, "MainTabVirtualMachineView_table_ConsoleConnectCommand")]/div/div[2]')
    c = driver.find_element(
        By.CSS_SELECTOR, 'div[id$=MainTabVirtualMachineView_table_ConsoleConnectCommand] div div:nth-child(3)').click()
    a.click()
    b.get_attribute('innerHTML')
