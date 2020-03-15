from conan.packager import ConanMultiPackager
import copy
import platform

if __name__ == "__main__":
    builder = ConanMultiPackager(clang_versions=["9.0"], gcc_versions=["9.2"])
    builder.add_common_builds(shared_option_name="leveldb:shared", pure_c=False)    
    if platform.system() == "Linux":
        filtered_builds = []
        for settings, options, _, _, _ in builder.items:
            if settings["arch"] != "x86":
                filtered_builds.append([settings, options])
            if settings["compiler"] == "gcc" and float(settings["compiler.version"]) > 5:
                settings["compiler.libcxx"] = "libstdc++11"
        builder.builds = filtered_builds
    builder.run()

