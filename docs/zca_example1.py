#!/usr/bin/python

# This approach is used in tp-spice.

import pprint

from zope import interface  # pylint: disable=F0401
from zope.interface import adapter

registry = adapter.AdapterRegistry()


#pylint: disable=E0239
class IOSInfo(interface.Interface):
    pass

# OS type.


class IOSystem(IOSInfo):
    pass


pp = pprint.PrettyPrinter(indent=4)


def add_os_info(marker):
    def class_builder(cls):
        for c in cls.__bases__:
            registry.register([], c, marker, cls)
        return cls
    return class_builder

# add_os_info(marker="windows")(IWindows)
# It creates a class, and then apply to it a decorator. To class name.


@add_os_info(marker='windows')
class IWindows(IOSystem):
    pass


@add_os_info(marker='linux')
class ILinux(IOSystem):
    pass

# Linux distro.


@add_os_info(marker='rhel')
class IRhel(ILinux):
    pass


@add_os_info(marker='fedora')
class IFedora(ILinux):
    pass

# Architecture.


class IArch(IOSInfo):
    pass


@add_os_info(marker='32bits')
class IArch32(IArch):
    pass


@add_os_info(marker='64bits')
class IArch64(IArch):
    pass

# Major version.


class IVersionMajor(IOSInfo):
    pass


@add_os_info(marker='6')
class IVersionMajor6(IVersionMajor):
    pass


@add_os_info(marker='7')
class IVersionMajor7(IVersionMajor):
    pass

# Minor version.


class IVersionMinor(IOSInfo):
    pass


@add_os_info(marker='1')
class IVersionMinor1(IVersionMinor):
    pass


a = registry.lookupAll([], IOSInfo)
print "All known OS interfaces: %s" % repr(a)

a = registry.lookup([], IVersionMajor, '7')
print repr(a)
