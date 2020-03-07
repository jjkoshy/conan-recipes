from conans import ConanFile, CMake, tools
import os


class LevelDBConan(ConanFile):
    name = "leveldb"
    version = "1.22"
    license = "https://github.com/google/leveldb/blob/master/LICENSE"
    url = "https://github.com/jjkoshy/conan-recipes/conan-leveldb"
    settings = "os", "compiler", "build_type", "arch"
    options = {
            "shared": [True, False],
            "with_snappy": [True, False] }
    default_options = {
            "shared": False,
            "with_snappy": False }
    generators = "cmake"

    # This exists because leveldb conditionally includes code that uses snappy
    # i.e., if snappy is available on the system. If you wish to enable snappy
    # in leveldb, set with_snappy to True

    # leveldb conditionally includes tcmalloc and crc32c as well. We could add
    # these dependencies conditionally as well if there are conan packages
    # available for them.

    # if you have a recipe that depends on leveldb, set if you wish to have
    # snappy enabled, you will likely need to add the snappy lib location to
    # the library search path

    optional_snappy_requirement = "snappy/1.1.7@bincrafters/stable"

    def requirements(self):
        if self.options.with_snappy:
            self.requires(self.optional_snappy_requirement)
    
    @property
    def zipped_folder(self):
        return "leveldb-%s" % self.version

    def source(self):
       zip_name = "%s.zip" % self.version
       tools.download("https://github.com/google/leveldb/archive/%s.zip" % self.version, zip_name)
       tools.check_md5(zip_name, "f741bc416308adb35d79900afe282d9e")
       tools.unzip(zip_name)
       os.unlink(zip_name)
       with tools.chdir(self.zipped_folder):
           if not self.options.with_snappy:
               tools.replace_in_file("CMakeLists.txt",
                       '''check_library_exists(snappy snappy_compress "" HAVE_SNAPPY)''',
                       '''check_library_exists(snappy snappy_compress "" IGNORE_HAVE_SNAPPY)''')


    def build(self):
        cmake = CMake(self)
        cmake.configure(
            source_folder=self.zipped_folder,
            defs={
                'CMAKE_POSITION_INDEPENDENT_CODE': True
            })
        cmake.build()

    def package(self):
        self.copy("*", dst="include", src="%s/include" % self.zipped_folder, keep_path=True)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("LICENSE", src=self.zipped_folder, dst="", keep_path=False)
           
        if self.options.shared:
            self.copy("*.dll", dst="bin", keep_path=False)
            self.copy("*.so*", dst="lib", keep_path=False)
        else:
            self.copy("*.a", dst="lib", keep_path=False)


    def package_info(self):
        self.cpp_info.libs = ["leveldb"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
