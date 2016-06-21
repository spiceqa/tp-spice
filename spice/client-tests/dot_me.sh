# Use:
# . <dot_me.sh>
npid=$(pgrep nautilus | head -n 1)
$(cat /proc/$npid/environ | xargs -n 1 -0 echo 'export' | grep DBUS)
export DISPLAY=":0.0"
