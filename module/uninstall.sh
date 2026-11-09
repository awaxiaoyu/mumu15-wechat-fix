#!/system/bin/sh
# Running WeChat processes retain their private mount until they exit/reboot.
rm -f /data/local/tmp/wechat-media-provider.so
