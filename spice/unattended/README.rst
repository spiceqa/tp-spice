=======================================================
How to create a new kickstart file for RedHat products.
=======================================================

- Install RPMs:

    - system-config-kickstart
    - pykickstart

- Run **system-config-kickstart**.
- Save a new template.
- Add %packages, %pre, %post sections.
- Add necessary options, consult with: /usr/share/doc/pykickstart-1.99.66.6/kickstart-docs.rst
- Validate a new kickstart file with **ksvalidator**


=====
Links
=====

http://pbraun.nethence.com/unix/sysutils_linux/kickstart.html

pykickstart 1.99 (RHEL7)
------------------------

https://github.com/rhinstaller/pykickstart/blob/rhel7-branch/docs/kickstart-docs.rst

pykickstart 1.74 (RHEL6)
------------------------

https://github.com/rhinstaller/pykickstart/blob/rhel6-branch/docs/kickstart-docs.txt
http://www.linuxtopia.org/online_books/rhel6/rhel_6_installation/rhel_6_installation_s1-kickstart2-options.html
