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


"""General UI-related exceptions module Make sure all user-defined exception
inherits from GeneralException.
"""


class GeneralException(Exception):
    """Base class for user defined exceptions.
    """
    message = "General Exception"

    def __init__(self, *value):
        self.value = value

    def __str__(self):
        return "%s: %s" % (self.message,
                           repr(self.value[0] if len(self.value) == 1
                                else self.value))

    def __repr__(self):
        return "%s(%s: %s)" % (self.__class__.__name__, self.message,
                               repr(self.value[0] if len(self.value) == 1
                                    else self.value))


class InitPageValidationError(GeneralException):
    """Initial validation error upon PageObject creation.
    """
    message = "Initial page validation error"


class UserActionError(GeneralException):
    """Base error class for all user action related errors.
    """
    message = "user action failed"


class FieldIsRequiredError(UserActionError):
    """Required input field is not filled.  Input field can be input text,
    select box, radio button, etc.
    """
    message = "Field is required"


class LoginError(UserActionError):
    """Invalid username or password provided.
    """
    message = "Login Failed"


class ButtonIsDisabledError(GeneralException):
    """Button widget is disabled.
    """
    message = "button is disabled"


class ElementCreationError(UserActionError):
    """Element creation failed.
    """
    message = "error creating element"


class ElementUpdateError(UserActionError):
    """Element update failed.
    """
    message = "error update element"


class ElementRemovalError(UserActionError):
    """Element removal failed.
    """
    message = "error removing element"


class ElementExportError(UserActionError):
    """Element export failed.
    """
    message = "Error exporting element"


class ElementDoesNotExistError(GeneralException):
    """Element does not exist.
    """
    message = "element does not exist"


class InvalidConfigParamError(GeneralException):
    """Invalid or missing configuration parameter.
    """
    message = "config parameter not found"


class WaitTimeoutError(GeneralException):
    """Wait timeout expired.
    """
    message = "timeout expired"


class ElementIsNotClickableError(GeneralException):
    """Element is not clickable at this poit.  Either is not visible (yet) or
    is overlapped by another element.
    """
    pass
