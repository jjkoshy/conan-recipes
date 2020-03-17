from conans import CMake, ConanFile, tools
import os


class BrpcConan(ConanFile):
    name = "brpc"
    version = "0.9.5"
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
    generators = ("cmake_paths")
    requires = ("gflags/2.2.2@bincrafters/stable",
                "protobuf/3.6.1@bincrafters/stable",
                "leveldb/1.22@jjkoshy/stable",
                "protoc_installer/3.6.1@bincrafters/stable")

    def config(self):
        # can also be passed via conan invocation. e.g.,
        # conan create ... -o protobuf:shared=True
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

            # since a conan profile may specify building packages in debug
            # mode, add the debug name of libgflags
            repl = "GFLAGS_LIBRARY NAMES gflags libgflags"
            tools.replace_in_file("cmake/FindGFLAGS.cmake", repl,
                    repl + " gflags_debug libgflags_debug")

            # conan recipes publish libraries with lower case names (see
            # https://github.com/conan-io/conan/issues/4460 for e.g.,) so we
            # have to replace GFLAGS with gflags
            repl = "find_package(GFLAGS REQUIRED)"
            tools.replace_in_file("CMakeLists.txt", repl,
                    "\n".join(["find_package(gflags REQUIRED)",
                               "include(FindGFLAGS)"]))

            # we are using the cmake_paths generator which sets the
            # CMAKE_MODULE_PATH. Unfortunately, brpc's CMakeLists.txt
            # overwrites it with set. So we replace the set with an append.
            tools.replace_in_file("CMakeLists.txt", "set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)",
                '''list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")''')

            # brpc's CMakeLists.txt uses git to figure out what to set
            # BRPC_REVISION to. Since the recipe fetches a release zip we just
            # set it manually and remove the call to git
            repl = "project(brpc C CXX)"
            tools.replace_in_file("CMakeLists.txt", repl,
                    "\n".join([repl, '''set(BRPC_REVISION "a6ccc96a")''']))
            tools.replace_in_file("CMakeLists.txt", """git rev-parse --short HEAD | tr -d '\\n'""", ":")
            tools.replace_in_file("CMakeLists.txt", "OUTPUT_VARIABLE BRPC_REVISION", "")

            # (i) many linux distributions come with protobuf installed. Since
            # this recipe explicitly specifies a dependency on the bincrafters
            # protobuf package, we want to use that package (not the locally
            # available libprotobuf). (ii) conan-protobuf publishes the protoc
            # compiler and libprotobuf separately so we find_package for both.
            # (iii) since brpc uses the older style calls to protoc, we have to
            # turn on the protobuf_MODULE_COMPATIBLE option.
            tools.replace_in_file("CMakeLists.txt", "include(FindProtobuf)",
                    '''
list(APPEND CMAKE_PREFIX_PATH ${CMAKE_PREFIX_PATH}
    "${CONAN_PROTOBUF_ROOT}/lib/cmake/protobuf"
    "${CONAN_PROTOC_INSTALLER_ROOT}/lib/cmake/protoc")
option(protobuf_MODULE_COMPATIBLE "override" ON)
find_package(protoc REQUIRED)
find_package(protobuf REQUIRED)''')

            # include the debug name of protoc in case the conan profile
            # specifies debug mode. also, search for snappy lib if with_snappy
            # is true
            tools.replace_in_file("CMakeLists.txt", "find_library(PROTOC_LIB NAMES protoc)",
                    ('''
find_library(SNAPPY_LIB NAMES snappy)
''' if self.options.with_snappy else "") + '''
find_library(PROTOC_LIB NAMES protoc protocd)
set(PROTOBUF_INCLUDE_DIRS "${CONAN_PROTOBUF_ROOT}/include")
set(PROTOBUF_INCLUDE_DIR "${CONAN_PROTOBUF_ROOT}/include")''')
            tools.replace_in_file("CMakeLists.txt", "${PROTOBUF_LIBRARIES}", "${Protobuf_LIBRARIES}")

            # add snappy to list of libs to link with if with_snappy is true
            if self.options.with_snappy:
                repl = "${OPENSSL_CRYPTO_LIBRARY}"
                tools.replace_in_file("CMakeLists.txt", repl, repl + '''
    ${SNAPPY_LIB}''')

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

