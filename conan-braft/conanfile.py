from conans import CMake, ConanFile, tools
import os

class BraftConan(ConanFile):
    name = "braft"
    version = "1.0.2"
    license = "https://github.com/baidu/braft/blob/master/LICENSE"
    description = "An industrial-grade C++ implementation of RAFT consensus algorithm based on brpc"
    settings = "os", "os_build", "compiler", "build_type", "arch", "arch_build"
    options = {
            "shared": [True, False],
            "with_snappy": [True, False] }
    default_options = {
            "shared": False,
            "with_snappy": False }
    generators = ("cmake_paths")
    requires = ("gflags/2.2.2@bincrafters/stable",
                "leveldb/1.22@jjkoshy/stable",
                "brpc/0.9.5@jjkoshy/stable")
    exports_sources = "braft-%s/*" % version

    def config(self):
        self.options['gflags'].shared = True
        self.options['gflags'].nothreads = False
        self.options['leveldb'].with_snappy = self.options.with_snappy

    @property
    def zip_folder_name(self):
        return "%s-%s" % (self.name, self.version)

    def source(self):
        zip_name = "%s.zip" % self.version
        tools.download("https://github.com/baidu/braft/archive/v%s.zip" % self.version, zip_name)
        tools.unzip(zip_name)
        tools.check_md5(zip_name, "446c4b4304190fb7e50cf62eb1a50ac0")
        os.unlink(zip_name)
        with tools.chdir(self.zip_folder_name):
            repl = "GFLAGS_LIB NAMES gflags"
            tools.replace_in_file("CMakeLists.txt",
                    repl, repl + " gflags_debug libgflags_debug")

    def configure_cmake(self):
        cmake = CMake(self)
        # uncomment for non-parallel builds
        # cmake.parallel = False
        # cmake_paths generator produces conan_paths.cmake
        cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = "conan_paths.cmake"
        cmake.configure(
            source_folder = "braft-1.0.2",
            defs={
                'CMAKE_POSITION_INDEPENDENT_CODE': True,
            })
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", "braft-%s" % self.version, keep_path=False)
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["brpc"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

