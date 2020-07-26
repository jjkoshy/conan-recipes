from conans import CMake, ConanFile, tools
import os


class BrpcConan(ConanFile):
    name = "brpc"
    version = "0.9.6"
    license = "https://github.com/apache/incubator-brpc/blob/master/LICENSE"
    url = "https://github.com/jjkoshy/conan-recipes/conan-brpc"
    description = "An industrial-grade RPC framework used throughout Baidu"
    settings = "os", "os_build", "compiler", "build_type", "arch", "arch_build"
    options = {
            "shared": [True, False],
            # see the leveldb recipe in conan-leveldb/conanfile.py for why we
            # need this
            "with_snappy": [True, False] }
    default_options = {
            "shared": False,
            "with_snappy": False }
    # cmake_paths generates a file which we set as the cmake toolchain file
    generators = ("cmake", "cmake_paths", "cmake_find_package")
    exports_sources = ["CMakeLists.txt", "patches/*"]

    requires = ("gflags/2.2.2",
                "protobuf/3.9.1",
                "leveldb/1.22")

    def config(self):
        # can also be passed via conan invocation. e.g.,
        # conan create ... -o protobuf:shared=True
        self.options['gflags'].shared = True
        self.options['gflags'].nothreads = False
        # TODO figure out if we need with_ options for zlib
        self.options['protobuf'].with_zlib = True
        self.options['protobuf'].shared = True
        self.options['leveldb'].with_snappy = self.options.with_snappy

    @property
    def zip_folder_name(self):
        return "incubator-%s-%s" % (self.name, self.version)

    def source(self):
        zip_name = "%s.zip" % self.version
        tools.download("https://github.com/apache/incubator-brpc/archive/%s.zip" % self.version, zip_name)
        tools.unzip(zip_name)
        tools.check_md5(zip_name, "783b3b0d5b9d254a93f26ce769b00bfc")
        os.unlink(zip_name)
        with tools.chdir(self.zip_folder_name):
            # TODO: switch to conandata.yml approach
            tools.patch(patch_file="../patches/brpc-0.9.6.patch", strip=1)

            # add snappy to list of libs to link with if with_snappy is true
            if self.options.with_snappy:
                tools.patch(patch_file="../patches/snappy.patch", strip=1)

    def configure_cmake(self):
        cmake = CMake(self)
        # uncomment for non-parallel builds
        # cmake.parallel = False

        # The cmake_paths generator produces conan_paths.cmake which sets
        # various path variables for the libraries this recipe depends on, and
        # adds those to the CMAKE_MODULE_PATH (used by include() and
        # FindXXX.cmake) and CMAKE_PREFIX_PATH (used by find_library and
        # find_dependency). For e.g.:
        #
        # set(CONAN_ZLIB_ROOT "/home/jjkoshy/.conan/data/zlib/1.2.11/conan/stable/package/7c292f54b7e6c224f121c640404bf7fbbeb41a8f")
        # set(CMAKE_MODULE_PATH "/home/jjkoshy/.conan/data/brpc/0.9.5/jjkoshy/stable/package/3a1b935ee508ae45a4e5b45eb2504048debd5203/"
        #                       "/home/jjkoshy/.conan/data/gflags/2.2.2/bincrafters/stable/package/b79e8887815d0c32512f737644747a0a383a2545/"
        # ... )

        cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = "conan_paths.cmake"
        # TODO: the source_subfolder should be something generic like
        # src or source-subfolder, and we should rename. change
        # cmakelists.txt also
        cmake.configure(
            defs={
                'CMAKE_POSITION_INDEPENDENT_CODE': True,
                'protobuf_MODULE_COMPATIBLE': True
            })
        return cmake
    
    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", "incubator-brpc-0.9.6", keep_path=False)
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["brpc"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

