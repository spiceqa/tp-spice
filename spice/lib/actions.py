#!/usr/bin/python

import zope
from zope import interface
from zope.interface.interface import adapter_hooks
from zope.interface import adapter

registry = adapter.AdapterRegistry()


@interface.implementer(IVm)
class Vm(object):

    def __init__(self, cfg):
        self.cfg = cfg

# Runner

class IRunCmd(interface.Interface):
    def __call__(cmd):
        """Run command."""

@interface.implementer(IRunCmd)
class RunCmdOut(object):
    def __init__(self, ssn):
        self.ssn = ssn
    def __call__(self, cmd):
        return ssn.cmd_output(cmd)

# Command(s)

class IVmAction(interface.Interface):
    def __call__():
        """Run some command."""

class ActionBase(object):
    def __init__(self, run):
        self.run = run

@interface.implementer(IVmAction)
class ProcIsActive(ActionBase):
    def __call__(self, pname):
        arg = "IMAGENAME eq %s.exe" % pname
        cmd = ["tasklist", "/FI", arg]
        cmdout = self.run(cmd)
        if pname in cmdout:
            res = True
        else:
            res = False
        return res


# Command maker

class ICmdMaker(interface.Interface):
    def __call__(cmd):
        """Make a commandline, escaping arguments."""

@interface.implementer(ICmdMaker)
class CmdLine(object):
    def __call__(cmd):
        return subprocess.list2cmdline(cmd)


registry.register([IRhel, IVersionMajor7], IVmAction, 'proc_is_active', ProcIsActive)


vm.act.proc_is_active("bash")

act = Action(test, vm_name)




#scmd = ICommand(test, "Selenium") # two realization win + linux
#sel_cmd = scmd.make()
#
#
#
#@interface.implementer(ICommand)
#class CmdLineLinux(object):
#
#    def __init__(self, cmdline):
#        self.cmdline = cmdline
#
#    def mk_cmd(self):
#        return subprocess.list2cmdline(self.cmdline)
#
#
#def cmdline_invariant(cmdline):
#    if type(cmdline) not list:
#        raise CmdlineError(cmdline)
#
#
#class CmdLineError(zope.Interface.Invalid):
#    """A bogous cmdline."""
#    def __repr__(self):
#        return "Bad cmdline: %r" % self.args
#
#
#    defs = interface.Attribute("-Dxxx definitions.")
#    opts = interface.Attribute("Selenium server options.")
#    jar_rpath = interface.Attribute("Path to Selenium .jar file.")
#    java = interface.Attribute("Path to Java interpreter.")
#
#
#class ICmdLine(interface.Interface):
#
#    cmdline = interface.Attribute("Command and its options list.")
#
#    def mk_cmd():
#        """Make a string escaping it for passing to os.system() like calls.
#        """
#
#
#@interface.implementer(IExternalAPIPort)
#class SeleniumLinux(object, Commands):
#
#    def __init__(self):
#        self.defs = []
#        if self.cfg.selenium_driver == 'Firefox':
#            profile = self.cfg.firefox_profile
#            if profile:
#                cmd = "firefox -CreateProfile %s" % profile
#                output = self.ssn.cmd(cmd)
#                output = re.findall(r'\'[^\']*\'', output)[1]
#                output = output.replace("'",'')
#                output =  os.path.dirname(dirname)
#                self.firefox_profile_dir = output
#                self.vm.info("Created a new FF profile at: %s", output)
#                self.defs.append("-Dwebdriver.firefox.profile=%s" % profile)
#        self.opts = []
#        self.opts.append("-port %s" % cfg.selenium_port)
#        self.opts.append("-trustAllSSLcertificates")
#        self.java = "java"
#        selenium = download_asset("selenium", section=self.cfg_vm.selenium_ver)
#        fname = os.path.basename(selenium)
#        jar_rpath = os.path.join(self.workdir(), fname)
#        self.vm.copy_files_to(selenium, jar_rpath)
#
#    def mk_cmd(self):
#        cmd = "{java} {defs} -jar {dst_fname} {opts}".format(self.java,
#                                                             self.defs,
#                                                             self.dst_fname,
#                                                             self.opts)
#        self.vm.info("Selenium cmd: %s", cmd)
#
#    def run(self, session):
#        ssn.sendline(cmd)
#
#
#
#
#    def run(self, ssn):
#        """Some general info.
#        There are ways to define Firefox options globaly:
#
#            * /usr/lib64/firefox/defaults/preferences/<anyname>.js
#            * /etc/firefox/pref/<anyname>.js
#
#        Format is:
#
#            user_pref("some.key", "somevalue");
#            pref("some.key", "somevalue");
#
#        All values are defined at:
#
#            about:config?filter=color
#
#        Also user can define values for specific profile:
#
#            http://kb.mozillazine.org/Profile_folder_-_Firefox#Linux
#
#        For curent profile go to: about:support and press "Open Directory"
#
#        Selenium understands next options:
#
#            -Dwebdriver.firefox.profile=my-profile
#            -Dwebdriver.firefox.bin=/path/to/firefox
#            -trustAllSSLcertificates
#
#        Also it is possible to specify Firefox profile in selenium python
#        bindings:
#
#            FirefoxProfile p = new FirefoxProfile(new File("D:\\profile2"));
#            p.updateUserPrefs(new File("D:\\t.js"));
#
#        To create a new profile call:
#
#            firefox -CreateProfile <profile name>
#
#        """
#        selenium = download_asset("selenium", section=self.cfg_vm.selenium_ver)
#        fname = os.path.basename(selenium)
#        dst_fname = os.path.join(self.workdir(), fname)
#        self.vm.copy_files_to(selenium, dst_fname)

cfg1 = {'os':'Linux', 'distr':'RHEL', 'ver':'7', 'variant':'Workstation', 'arch':None}
cfg2 = {'os':'Windows', 'ver':'10', 'variant':'Professional'}

#IService(interface.Interface):
#    def start():
#        """Start service."""
#
#    def stop():
#        """Stop service."""
#
#    def restart():
#        """Stop service."""
#
#
#class ICmdKill(ICommand):
#    pass
#
#
#
#vm1 = Vm(cfg1)
#vm2 = Vm(cfg2)
#zope.interface.directlyProvides(foo_restart_rhel7, ICommandRestart)
#registry.register([IVm], ICommandRestart, '', AdapterVm2Cmd_Factory(ICommandRestart))
#registry.register([IRhel, IVersionMajor7], ICommandRestart, '', foo_restart_rhel7)

#class AdapterVm2Cmd_Factory(object):
#    """
#    Returns
#    -------
#        Returns PROXY/ADAPTER, that takes IVM
#    """
#
#    def __init__(self, req_iface):
#        self.req_iface = req_iface
#
#    def __call__(self, vm_provider):
#        # IRhel
#        os = registry.lookup([], IOSystem, cfg.os)
#        ver = registry.lookup([], IVersionMajor, cfg.ver)
#        mver = registry.lookup([], IVersionMajor, cfg.ver)
#        arch = registry.lookup([], IArch, cfg.ver)
#        f = registry.lookup([os, ver, mver, arch], self.req_iface) or \
#            registry.lookup([os, ver, mver], self.req_iface) or \
#            registry.lookup([os, ver, arch], self.req_iface) or \
#            registry.lookup([os, ver], self.req_iface) or \
#            registry.lookup([os], self.req_iface)
#        return f
