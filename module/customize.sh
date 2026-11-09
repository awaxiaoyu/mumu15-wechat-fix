#!/system/bin/sh

[ "$BOOTMODE" = true ] || abort '! Install this module from the KernelSU app.'
# MuMu may report aarch64 through uname while its primary Android ABI is x86_64.
[ "$(getprop ro.product.cpu.abi)" = x86_64 ] || abort '! Only x86_64 MuMu is supported.'
[ "$(getprop ro.build.version.sdk)" = 35 ] || abort '! Only Android 15 / SDK 35 has been verified.'

SOURCE=/system/lib64/libhoudini.so
ORIGINAL_SHA=b0132bc4c7c6351d6daecae51c19fb779408f0e34432310f13c48cb75c034f4d
PATCHED_SHA=9b0d18c457cb6d874e6fc95871b8e2d5659809de8257e623861e52f9ddaeb29d

set -- $(sha256sum "$SOURCE")
[ "$1" = "$ORIGINAL_SHA" ] || abort '! Unsupported MuMu translator build; original SHA256 does not match.'

ui_print '- Generating the media provider patch from this device...'
cp "$SOURCE" "$MODPATH/libhoudini.so" || abort '! Cannot copy the original library.'
printf '\130' | dd of="$MODPATH/libhoudini.so" bs=1 seek=7387548 count=1 conv=notrunc 2>/dev/null || abort '! Cannot apply the patch.'
set -- $(sha256sum "$MODPATH/libhoudini.so")
[ "$1" = "$PATCHED_SHA" ] || abort '! Patched library SHA256 does not match.'

# Do not reuse a verification marker from an older installation.
rm -f "$MODPATH/verified" "$MODPATH/last-boot.log"
set_perm_recursive "$MODPATH" 0 0 0755 0644
set_perm "$MODPATH/post-fs-data.sh" 0 0 0755
set_perm "$MODPATH/uninstall.sh" 0 0 0755
ui_print '- Ready. Reboot to enable the WeChat-only repair.'
