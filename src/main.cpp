#include <sys/types.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/mount.h>
#include <sys/wait.h>
#include <sched.h>
#include "zygisk.hpp"

extern "C" int __android_log_print(int, const char *, const char *, ...);
struct Request { int pid; unsigned long namespace_inode; };
static void root_companion(int socket) {
    Request request{};
    if (read(socket, &request, sizeof(request)) != sizeof(request) || request.pid <= 1) return;
    pid_t worker = fork();
    if (worker == 0) {
        char target[80];
        snprintf(target, sizeof(target), "/proc/%d/ns/mnt", request.pid);
        for (int attempt = 0; attempt < 500; ++attempt) {
            struct stat st{};
            if (stat(target, &st) != 0) _exit(1);
            if (st.st_ino != request.namespace_inode) {
                int ns = open(target, O_RDONLY | O_CLOEXEC);
                int result = ns < 0 ? -1 : setns(ns, CLONE_NEWNS);
                if (ns >= 0) close(ns);
                if (result == 0) result = mount("/data/local/tmp/wechat-media-provider.so", "/system/lib64/libhoudini.so", nullptr, MS_BIND, nullptr);
                __android_log_print(result == 0 ? 4 : 6, "WeChatMediaFix", "WeChat namespace mount: %s pid=%d", result == 0 ? "applied" : "failed", request.pid);
                _exit(result == 0 ? 0 : 1);
            }
            usleep(10000);
        }
        __android_log_print(6, "WeChatMediaFix", "App namespace did not change pid=%d", request.pid);
        _exit(1);
    }
    if (worker > 0) waitpid(worker, nullptr, 0);
}
static void *(*original_dlopen)(const char *, int);
static void *wechat_dlopen(const char *name, int flags) {
    if (name && (strcmp(name, "/system/lib64/libhoudini.so") == 0 || strcmp(name, "libhoudini.so") == 0)) {
        struct stat source{}, target{};
        if (stat("/data/local/tmp/wechat-media-provider.so", &source) == 0) {
            for (int attempt = 0; attempt < 500; ++attempt) {
                if (stat("/system/lib64/libhoudini.so", &target) == 0 && source.st_ino == target.st_ino && source.st_dev == target.st_dev) break;
                usleep(10000);
            }
        }
    }
    return original_dlopen(name, flags);
}

class WeChatMediaFix : public zygisk::ModuleBase {
    zygisk::Api *api = nullptr;
    JNIEnv *env = nullptr;
public:
    void onLoad(zygisk::Api *a, JNIEnv *e) override { api = a; env = e; }
    void preAppSpecialize(zygisk::AppSpecializeArgs *args) override {
        const char *name = env->GetStringUTFChars(args->nice_name, nullptr);
        if (!name) return;
        bool selected = strncmp(name, "com.tencent.mm", 14) == 0 && (name[14] == 0 || name[14] == ':');
        env->ReleaseStringUTFChars(args->nice_name, name);
        if (!selected) { api->setOption(zygisk::DLCLOSE_MODULE_LIBRARY); return; }
        __android_log_print(4, "WeChatMediaFix", "WeChat setup pid=%d", getpid());

        int dir = api->getModuleDir();
        if (dir < 0) { __android_log_print(6, "WeChatMediaFix", "No module directory"); return; }
        int ready = openat(dir, "verified", O_RDONLY | O_CLOEXEC);
        if (ready < 0) { close(dir); __android_log_print(6, "WeChatMediaFix", "No verification marker"); return; }
        close(ready);
        close(dir);
        int companion = api->connectCompanion();
        struct stat namespace_stat{};
        if (companion < 0 || stat("/proc/self/ns/mnt", &namespace_stat) != 0) {
            if (companion >= 0) close(companion);
            __android_log_print(6, "WeChatMediaFix", "No root companion");
            return;
        }
        Request request{getpid(), namespace_stat.st_ino};
        write(companion, &request, sizeof(request));
        close(companion);
        FILE *maps = fopen("/proc/self/maps", "r");
        if (!maps) return;
        char line[1024];
        bool installed = false;
        while (fgets(line, sizeof(line), maps)) {
            if (!strstr(line, "/system/lib64/libnb.so")) continue;
            unsigned major = 0, minor = 0;
            unsigned long inode = 0;
            if (sscanf(line, "%*s %*s %*s %x:%x %lu", &major, &minor, &inode) != 3) break;
            dev_t dev = ((major & 0xfff) << 8) | (minor & 0xff) | ((minor & ~0xffUL) << 12);
            api->pltHookRegister(dev, inode, "dlopen", (void *)wechat_dlopen, (void **)&original_dlopen);
            installed = api->pltHookCommit();
            break;
        }
        fclose(maps);
        __android_log_print(installed ? 4 : 6, "WeChatMediaFix", "WeChat loader hook: %s pid=%d", installed ? "applied" : "failed", getpid());
    }
};

REGISTER_ZYGISK_MODULE(WeChatMediaFix)
REGISTER_ZYGISK_COMPANION(root_companion)
