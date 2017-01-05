#!/usr/bin/python

# This file shows Zope interfaces in work.
# This approach is not used in tp-spice.

import zope
from zope import interface
from zope.interface import adapter

registry = adapter.AdapterRegistry()


class MetaMarker(zope.interface.interface.InterfaceClass):
    def __init__(cls, name, bases, attrs):
        key = 'marker'
        if '__metaclass__' in attrs:
            del attrs['__metaclass__']
        if key in attrs:
            val = attrs[key]
            del attrs[key]
            for base in bases:
                registry.register([], base, val, cls)
        super(MetaMarker, cls).__init__(name, bases, attrs)


class IOSInfo(interface.Interface):
    # If this technique fails sometime due to Python incompabity you always
    # can use next call just in place IClass definition:
    # registry.registry([], IVersionMajor, '7', IVersionMajor7)
    # https://blogs.gnome.org/jamesh/2005/09/08/python-class-advisors/
    __metaclass__ = MetaMarker

# OS type.


class IOSystem(IOSInfo):
    pass


class IWindows(IOSystem):
    marker = 'windows'


class ILinux(IOSystem):
    marker = 'linux'

# Linux distro.


class IRhel(ILinux):
    marker = "rhel"


class IFedora(ILinux):
    marker = "fedora"

# Architecture.


class IArch(IOSInfo):
    pass


class IArch32(IArch):
    marker = "32bits"


class IArch64(IArch):
    marker = "64bits"

# Major version.


class IVersionMajor(IOSInfo):
    pass


class IVersionMajor6(IVersionMajor):
    marker = "6"


class IVersionMajor7(IVersionMajor):
    marker = "7"

# Minor version.


class IVersionMinor(IOSInfo):
    pass


class IVersionMinor1(IVersionMinor):
    marker = "1"


a = registry.lookupAll([], IOSInfo)
print a

a = registry.lookup([], IVersionMajor, '7')
print a
