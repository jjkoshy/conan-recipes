from conans import ConanFile, CMake, tools
import os


class LevelDBConan(ConanFile):
    name = "leveldb"
    version = "1.22"
    license = "https://github.com/google/leveldb/blob/master/LICENSE"
    url = "https://github.com/jjkoshy/conan-recipes/conan-leveldb"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    requires = ("snappy/1.1.7@bincrafters/stable")
    
    @property
    def zipped_folder(self):
        return "leveldb-%s" % self.version

    def config(self):
        self.options['snappy'].shared = True
    
    def source(self):
       tools.download("https://github.com/google/leveldb/archive/%s.zip" % self.version, "leveldb.zip")
       tools.unzip("leveldb.zip")

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
