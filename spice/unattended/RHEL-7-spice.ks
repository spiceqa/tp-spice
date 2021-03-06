#
# Next part was generated by system-config-kickstart.
#
#platform=x86, AMD64, or Intel EM64T
#version=DEVEL
# Install OS instead of upgrade
install
# Keyboard layouts
keyboard 'us'
# Root password
rootpw --plaintext 123456
# System timezone
timezone Europe/Prague
# System language
lang en_US
# Firewall configuration
firewall --disabled
# System authorization information
auth  --useshadow  --passalgo=sha512
# Use text mode install
text
# SELinux configuration
selinux --enforcing
# Network information
network  --bootproto=dhcp --device=eth0
# System bootloader configuration
bootloader --location=mbr
# Clear the Master Boot Record
zerombr
# Partition clearing information
clearpart --all --initlabel

#
# Added options.
#
bootloader --location=mbr --append="console=tty0 console=ttyS0,115200" --timeout=1
services --disabled="rhnsd,rngd,bluetooth" --enabled="ovirt-guest-agent,chronyd"
user --name=test --password=123456 --groups=wheel --plaintext
xconfig --startxonboot
autopart --type=plain
poweroff
firstboot --disable

#
# Kdump.
#
%addon com_redhat_kdump --disable
%end

#
# Packages.
#
%packages --default --ignoremissing
@smart-card
spice-vdagent
virt-viewer
python-pillow
# Note
# ----
# Leave a note: why do you need a certain package when you add a new entry?
-gnome-initial-setup  # Remove initial pop-up diolog for fresh installed system.
-subscription-manager # Remove subscription tool for customers.
%end

#
# Post.
#
%post --erroronfail --log=/root/ks-post.log

#
# Remove password for root/test.
#
echo 'Remove password for root/test.'
passwd -d root
passwd -d test

#
# SSH permit login with empty passwords.
#
echo 'SSH permit login with empty passwords.'
sed -i '/PermitEmpty/aPermitEmptyPasswords yes' '/etc/ssh/sshd_config'

#
# Remove rhgb quiet in grub config.
#
echo 'Remove rhgb quiet in grub config.'
grubby --remove-args='rhgb quiet' --update-kernel="$(grubby --default-kernel)"

#
# Enable Gnome autologin.
#
echo 'Enable Gnome autologin.'
cat > '/etc/gdm/custom.conf' << EOF
[daemon]
AutomaticLogin=test
AutomaticLoginEnable=True
EOF

#
# Add yum repo.
#
url="$(cat '/proc/cmdline' | grep -oE 'http[^[:space:]]+')"
if [ -n "$url" ]; then
    echo 'Add yum repo.'
    cat > '/etc/yum.repos.d/install.repo' << EOF
[install]
name = install
baseurl = $url
enabled = 1
gpgcheck = 0
EOF
fi

#
# Disable screensaver for Gnome.
#
echo 'Disable screensaver for Gnome.'
cat > '/etc/dconf/db/local.d/screensaver' << EOF
[org/gnome/desktop/session]
idle-delay=uint32 0
[org/gnome/desktop/lockdown]
disable-lock-screen=true
[org/gnome/desktop/screensaver]
lock-enabled=false
[org/gnome/settings-daemon/plugins/power]
active=false
EOF
cat > '/etc/dconf/db/local.d/locks/screensaver' << EOF
/org/gnome/desktop/session/idle-delay
/org/gnome/desktop/lockdown/disable-lock-screen
/org/gnome/desktop/screensaver/lock-enabled
/org/gnome/settings-daemon/plugins/power/active
EOF
dconf update

#
# Add RedHat certificates.
#
certs[1]='https://password.corp.redhat.com/cacert.crt'
certs[2]='https://password.corp.redhat.com/RH-IT-Root-CA.crt'
certs[3]='http://idm.spice.brq.redhat.com/ipa/config/ca.crt'
i=1
for cert in "${certs[@]}"; do
    name="${i}.crt"
    wget -O "$name" "$cert"
    trust anchor "$name"
    i=$((i+1))
done

echo 'Post setup is finished.'
%end
