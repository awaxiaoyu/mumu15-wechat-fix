# MuMu Android 15 微信闪退修复

修复 MuMu Android 15 中微信登录后 `MediaCodec_loop` 的 native crash，保留 Android 15 和微信数据。

模块只对 `com.tencent.mm` 及其子进程生效。微信使用修复后的 ARM translator，其他 App 与 zygote 保持原库。安装包不包含 MuMu 的 `libhoudini.so`，安装时从设备原库生成一字节补丁。

## 已验证环境

| 组件 | 版本 |
| --- | --- |
| MuMu | 6.8.8.0 |
| Android | 15 / SDK 35 / x86_64 |
| 微信 | 8.0.80 |
| Root | KernelSU 32525 |
| Zygisk 实现 | Zygisk Next 1.5.2 |

**只支持下方 SHA256 对应的 MuMu 原库。** 其他构建尚未验证，校验不符时安装会停止；MuMu 升级改变原库后，模块会在下次开机时跳过修复。

## 安装

1. 在模拟器中启用 KernelSU 和 Zygisk Next。
2. 从 [Releases](https://github.com/awaxiaoyu/mumu15-wechat-fix/releases) 下载 `mumu15-wechat-fix-v2.1.0.zip`。
3. 在 KernelSU 模块页面从本地安装 ZIP，重启模拟器。
4. 打开微信。需要回退时，禁用本模块并重启。

不需要卸载微信、清除数据或降级系统。只发布 x86_64 模块；Magisk 及其他 Zygisk 实现尚未实机验证。

## 修复原理

复现时的崩溃链：

```text
MediaCodec_loop
  android::MediaCodec::setState
  __cfi_slowpath
  SIGSEGV / SEGV_ACCERR
```

崩溃寄存器与反汇编显示，native MediaCodec 使用的 `android::media::codec::provider_` 指向 ARM 空间的 vtable。MuMu 的 `libhoudini.so` 数据符号表含有同名映射；仅使这条映射失配后，登录后崩溃消失。这是实机对照得到的兼容修复，尚未对 MuMu 完整实现做源码验证。

| 项目 | 值 |
| --- | --- |
| 原符号 | `_ZN7android5media5codec9provider_E` |
| 补丁后 | `_ZN7android5media5codec9providerXE` |
| 字节偏移 | `0x70b99c` / `7387548` |
| 字节变化 | `0x5f` → `0x58` |
| 原库 SHA256 | `b0132bc4c7c6351d6daecae51c19fb779408f0e34432310f13c48cb75c034f4d` |
| 补丁库 SHA256 | `9b0d18c457cb6d874e6fc95871b8e2d5659809de8257e623861e52f9ddaeb29d` |

Zygisk 在微信进程创建时联系 root companion。companion 等待微信获得自己的 mount namespace，再将补丁库 bind mount 到该进程的 `/system/lib64/libhoudini.so`。对微信 `libnb.so` 的 `dlopen` hook 等待挂载完成后调用原始函数，保留 MuMu 的正常加载路径和时序。

**不要把补丁挂到 zygote 或全局 namespace。** 全局挂载曾导致另一个 App 启动退出；本模块因此使用微信独立 namespace。原系统镜像不会被覆盖，CFI 不会被禁用。

## 检查与回退

开机校验记录：

```sh
cat /data/adb/modules/mumu15_wechat_media_fix/last-boot.log
```

成功应显示：

```text
Verified. Zygisk will load the repair only inside WeChat processes.
```

查看微信进程挂载日志：

```sh
logcat -d -s WeChatMediaFix
```

可看到 `WeChat loader hook: applied` 和 `WeChat namespace mount: applied`。没有出现时，先核对 Zygisk 是否启用、原库校验是否通过。

KernelSU 中禁用模块后重启即可回退。root shell 也可执行：

```sh
touch /data/adb/modules/mumu15_wechat_media_fix/disable
reboot
```

## 其他微信问题

- **停在启动画面**：在同一 MuMu 构建中曾发现微信被套用了 Android 12 的 Galaxy Z Fold3 属性。需要单独检查 `/data/system/etc/mumu-configs/app-device-prop-android12.config`，只注释微信那条旧设备属性规则。此模块不会自动修改 MuMu 热更新配置。
- **微信授权提示“网络繁忙”**：本模块只解决媒体崩溃。在一套宿主 Clash TUN / MuMu 环境中，模拟器 IPv6 路径异常，切换 IPv4 后联系人同步及第三方微信登录恢复。需先验证自己的网络，本模块不会修改 IPv6、DNS、代理或登录状态。

## 从源码构建

依赖：Python 3.9+、CMake 3.22+、Android NDK r27c (`27.2.12479018`)；Windows 还需要将 Ninja 加入 PATH。使用 NDK 自带的 JNI headers，不需要额外 C++ 运行库。

Linux / macOS：

```sh
python3 scripts/build.py --ndk "$ANDROID_NDK_HOME"
```

Windows PowerShell：

```powershell
python scripts/build.py --ndk 'D:\Android\ndk\27.2.12479018'
```

产物位于 `dist/mumu15-wechat-fix-v2.1.0.zip`。GitHub Actions 使用同一入口构建并检查安装包。自行修改原生代码后，应在模拟器验证微信和其他 App 的 namespace；CI 不具备 MuMu 实机环境。

只生成补丁文件进行检查：

```sh
python3 scripts/patch_library.py /path/to/original/libhoudini.so /path/to/patched/libhoudini.so
```

该脚本先验证原库 hash，补丁后再核对目标 hash；不修改输入文件。

## 源码与许可

- 本项目原创代码：MIT License，见 [LICENSE](LICENSE)。
- Zygisk API header：来自 [topjohnwu/zygisk-module-sample](https://github.com/topjohnwu/zygisk-module-sample)，保留 ISC 风格许可和原版权声明，见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
- MuMu / Houdini 原库不随源码或安装包分发，安装程序仅使用当前设备上的原库。
