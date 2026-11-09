# Third-party notices

`third_party/zygisk/zygisk.hpp` is the unmodified public Zygisk API header from:

- Repository: https://github.com/topjohnwu/zygisk-module-sample
- Source revision: `8ce26128f81baaed0b969aaf7f52f886b61af4ab`
- Source path: `module/jni/zygisk.hpp`
- API version: 5

The header retains this license:

```text
Copyright 2022-2023 John "topjohnwu" Wu

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
```

Android NDK supplies the system and JNI headers at build time; they are not vendored here.
The MuMu/Houdini system library is not redistributed by this project. Its original and
patched hashes describe the supported input and output of the local patch operation.
