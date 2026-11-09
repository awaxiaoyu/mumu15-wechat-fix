#!/system/bin/sh
MODDIR=${0%/*}
rm -f "$MODDIR/verified"
date > "$MODDIR/last-boot.log"
set -- $(sha256sum /system/lib64/libhoudini.so)
if [ "$1" != b0132bc4c7c6351d6daecae51c19fb779408f0e34432310f13c48cb75c034f4d ]; then
    echo "Skipped: MuMu translator changed ($1)." >> "$MODDIR/last-boot.log"
    exit 0
fi
set -- $(sha256sum "$MODDIR/libhoudini.so")
if [ "$1" != 9b0d18c457cb6d874e6fc95871b8e2d5659809de8257e623861e52f9ddaeb29d ]; then
    echo 'Skipped: repair library checksum mismatch.' >> "$MODDIR/last-boot.log"
    exit 1
fi
chmod 644 "$MODDIR/libhoudini.so"
chcon u:object_r:system_lib_file:s0 "$MODDIR/libhoudini.so" || exit 1
cp "$MODDIR/libhoudini.so" /data/local/tmp/wechat-media-provider.so || exit 1
chmod 644 /data/local/tmp/wechat-media-provider.so
chcon u:object_r:system_lib_file:s0 /data/local/tmp/wechat-media-provider.so || exit 1
touch "$MODDIR/verified"
echo 'Verified. Zygisk will load the repair only inside WeChat processes.' >> "$MODDIR/last-boot.log"
