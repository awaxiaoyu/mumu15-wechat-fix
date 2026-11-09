cmake_minimum_required(VERSION 3.22)
project(wechat_media_fix LANGUAGES CXX)

if(NOT ANDROID OR NOT ANDROID_ABI STREQUAL "x86_64")
    message(FATAL_ERROR "Use the Android NDK toolchain with ANDROID_ABI=x86_64")
endif()

add_library(wechat_media_fix SHARED src/main.cpp)
target_compile_features(wechat_media_fix PRIVATE cxx_std_17)
target_include_directories(wechat_media_fix PRIVATE third_party/zygisk)
target_compile_definitions(wechat_media_fix PRIVATE _GNU_SOURCE)
target_compile_options(wechat_media_fix PRIVATE
    -Wall -Wextra -Werror -fvisibility=hidden -fno-exceptions -fno-rtti
    -fno-threadsafe-statics)
target_link_libraries(wechat_media_fix PRIVATE log)
target_link_options(wechat_media_fix PRIVATE -Wl,--no-undefined)
set_target_properties(wechat_media_fix PROPERTIES OUTPUT_NAME "wechat_media_fix")
