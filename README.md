# conan-recipes

This is a staging repo for a couple of [conan](https://conan.io/) recipes I'm
trying out in order to get a feel for conan.

## Quickstart

### Prepare a virtualenv/venv

Create a
[virtualenv](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
(or venv if you are using Python > 3.3).

Inside the virtualenv:
```
pip install conan
pip install conan-package-tools
```

### (Optional) Create a conan profile

I generally create a conan profile to switch between toolchains. Here is a
conan profile for an llvm toolchain:
```
conan profile show conan-clang
Configuration for profile conan-clang:

[settings]
compiler=clang
compiler.version=7.0
compiler.libcxx=libstdc++11
arch=x86_64
arch_build=x86_64
os=Linux
os_build=Linux
[options]
[build_requires]
[env]
CC=clang
CXX=clang++
```

(You can see the settings that are available in `~/.conan/settings.yml`.)

Additionally, you may want to check that you have suitable conan remotes to
fetch packages that you depend on. For example:

```
conan remote list
# returns:
conan-center: https://conan.bintray.com [Verify SSL: True]
bincrafters: https://api.bintray.com/conan/bincrafters/public-conan [Verify SSL: True]
```

### Create packages from the recipes

For example, for the leveldb package run this from the conan-leveldb recipe
directory:

`conan create . jjkoshy/stable -pr conan-clang --build missing`

Use a similar command for the other packages, although some recipes depend on
the others. E.g., you would need to create the leveldb package before creating
the brpc package.
