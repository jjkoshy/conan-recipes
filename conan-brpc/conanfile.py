from conans import CMake, ConanFile, tools
import os, shutil


class BrpcConan(ConanFile):
    name = "brpc"
    version = "0.9.5"
    license = "https://github.com/apache/incubator-brpc/blob/master/LICENSE"
    url = "https://github.com/jjkoshy/conan-recipes/conan-brpc"
    description = "An industrial-grade RPC framework used throughout Baidu"
    settings = "os", "os_build", "compiler", "build_type", "arch", "arch_build"
    options = {
            "shared": [True, False],
            "with_snappy": [True, False] }
    default_options = {
            "shared": False,
            "with_snappy": False }
    generators = ("cmake_paths")
    requires = ("gflags/2.2.2@bincrafters/stable",
                "protobuf/3.6.1@bincrafters/stable",
                "leveldb/1.22@jjkoshy/stable",
                "protoc_installer/3.6.1@bincrafters/stable")

    def config(self):
        self.options['gflags'].shared = True
        self.options['gflags'].nothreads = False
        self.options['protobuf'].with_zlib = True
        self.options['leveldb'].with_snappy = self.options.with_snappy

    @property
    def zip_folder_name(self):
        return "incubator-%s-%s" % (self.name, self.version)

    def source(self):
        zip_name = "%s.zip" % self.version
        tools.download("https://github.com/apache/incubator-brpc/archive/%s.zip" % self.version, zip_name)
        tools.unzip(zip_name)
        tools.check_md5(zip_name, "b9d4bf31e0820854fd14be9cc94f4150")
        os.unlink(zip_name)
        with tools.chdir(self.zip_folder_name):
            # tools.patch API is more convenient, but replace_in_file is more
            # robust (e.g., if you want to use this recipe for a newer brpc
            # version)
            repl = "GFLAGS_LIBRARY NAMES gflags libgflags"
            tools.replace_in_file("cmake/FindGFLAGS.cmake", repl,
                    repl + " gflags_debug libgflags_debug")
            tools.replace_in_file("CMakeLists.txt", "set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)",
                '''list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")''')
            repl = "find_package(GFLAGS REQUIRED)"
            tools.replace_in_file("CMakeLists.txt", repl,
                    "\n".join(["find_package(gflags REQUIRED)",
                               "include(FindGFLAGS)"]))
            tools.replace_in_file("CMakeLists.txt", """git rev-parse --short HEAD | tr -d '\\n'""", ":")
            tools.replace_in_file("CMakeLists.txt", "OUTPUT_VARIABLE BRPC_REVISION", "")
            repl = "project(brpc C CXX)"
            tools.replace_in_file("CMakeLists.txt", repl,
                    "\n".join([repl, '''set(BRPC_REVISION "a6ccc96a")''']))
            tools.replace_in_file("CMakeLists.txt", "include(FindProtobuf)",
                    '''
list(APPEND CMAKE_PREFIX_PATH ${CMAKE_PREFIX_PATH}
    "${CONAN_PROTOBUF_ROOT}/lib/cmake/protobuf"
    "${CONAN_PROTOC_INSTALLER_ROOT}/lib/cmake/protoc")
option(protobuf_MODULE_COMPATIBLE "override" ON)
find_package(protoc REQUIRED)
find_package(protobuf REQUIRED)''')
            tools.replace_in_file("CMakeLists.txt", "find_library(PROTOC_LIB NAMES protoc)",
                    '''
find_library(PROTOC_LIB NAMES protoc protocd)
set(PROTOBUF_INCLUDE_DIRS "${CONAN_PROTOBUF_ROOT}/include")
set(PROTOBUF_INCLUDE_DIR "${CONAN_PROTOBUF_ROOT}/include")''')
            tools.replace_in_file("CMakeLists.txt", "${PROTOBUF_LIBRARIES}", "${Protobuf_LIBRARIES}")

    def configure_cmake(self):
        cmake = CMake(self)
        # uncomment for non-parallel builds
        # cmake.parallel = False
        # cmake_paths generator produces conan_paths.cmake
        cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = "conan_paths.cmake"
        cmake.configure(
            source_folder="incubator-brpc-0.9.5",
            defs={
                'CMAKE_POSITION_INDEPENDENT_CODE': True,
            })
        return cmake
    
    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", "incubator-brpc-0.9.5", keep_path=False)
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["brpc"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

