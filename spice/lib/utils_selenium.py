class CommandsLinuxSelenium(Commands):

    def run_selenium(self, ssn):
        """Some general info.
        There are ways to define Firefox options globaly:

            * /usr/lib64/firefox/defaults/preferences/<anyname>.js
            * /etc/firefox/pref/<anyname>.js

        Format is:

            user_pref("some.key", "somevalue");
            pref("some.key", "somevalue");

        All values are defined at:

            about:config?filter=color

        Also user can define values for specific profile:

            http://kb.mozillazine.org/Profile_folder_-_Firefox#Linux

        For curent profile go to: about:support and press "Open Directory"

        Selenium understands next options:

            -Dwebdriver.firefox.profile=my-profile
            -Dwebdriver.firefox.bin=/path/to/firefox
            -trustAllSSLcertificates

        Also it is possible to specify Firefox profile in selenium python
        bindings:

            FirefoxProfile p = new FirefoxProfile(new File("D:\\profile2"));
            p.updateUserPrefs(new File("D:\\t.js"));

        To create a new profile call:

            firefox -CreateProfile <profile name>

        """
        selenium = download_asset("selenium", section=self.cfg_vm.selenium_ver)
        fname = os.path.basename(selenium)
        dst_fname = os.path.join(self.workdir(), fname)
        self.vm.copy_files_to(selenium, dst_fname)
        defs = []
        opts = []
        opts.append("-port %s" % cfg.selenium_port)
        opts.append("-trustAllSSLcertificates")
        if self.cfg.selenium_driver == 'Firefox':
            profile = self.cfg.firefox_profile
            if profile:
                cmd = "firefox -CreateProfile %s" % profile
                output = self.ssn.cmd(cmd)
                output = re.findall(r'\'[^\']*\'', output)[1]
                output = output.replace("'",'')
                output =  os.path.dirname(dirname)
                self.firefox_profile_dir = output
                self.vm.info("Created a new FF profile at: %s", output)
                defs.append("-Dwebdriver.firefox.profile=%s" % profile)
        defs = " ".join(defs)
        opts = " ".join(opts)
        cmd = "java {} -jar {} {}".format(defs, dst_fname, opts)
        self.vm.info("selenium cmd: %s", cmd)
        ssn.sendline(cmd)
