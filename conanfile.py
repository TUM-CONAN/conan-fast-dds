from conans import ConanFile, CMake, tools
import os, shutil

class FastDDSConan(ConanFile):
    name = "Fast-DDS"
    version = "2.0.0"
    license = "Apache License 2.0"
    author = "Frieder Pankratz"
    url = "https://github.com/TUM-CONAN/conan-fast-dds.git"
    description = "Conan wrapper for Fast-DDS"    
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": True}
    generators = "cmake"

    requires = ("Fast-CDR/1.0.14@camposs/stable","foonathan-memory/1.0.0@camposs/stable", "asio/1.16.1", "tinyxml2/8.0.0")
    

    def source(self):
        git = tools.Git()        
        git.clone("https://github.com/eProsima/Fast-DDS.git", "v%s" % self.version)

        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly        
        tools.replace_in_file("CMakeLists.txt", "project(fastrtps VERSION \"${PROJECT_VERSION}\" LANGUAGES C CXX)",
                              '''project(fastrtps VERSION "${PROJECT_VERSION}" LANGUAGES C CXX)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
set(TINYXML2_LIBRARY ${CONAN_LIBS_TINYXML2})
set(TINYXML2_INCLUDE_DIR ${CONAN_INCLUDE_DIRS_TINYXML2})
''')
        tools.replace_in_file("CMakeLists.txt", "project(fastrtps VERSION \"${LIB_VERSION_STR}\" LANGUAGES C CXX)",
                              '''project(fastrtps VERSION "${LIB_VERSION_STR}" LANGUAGES C CXX)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
set(TINYXML2_LIBRARY ${CONAN_LIBS_TINYXML2})
set(TINYXML2_INCLUDE_DIR ${CONAN_INCLUDE_DIRS_TINYXML2})
''')

    def configure(self):                        
        self.options['tinyxml2'].shared = self.options.shared
        self.options['Fast-CDR'].shared = self.options.shared

    def _configure_cmake(self):        
        cmake = CMake(self)
        cmake.verbose = True

        def add_cmake_option(option, value):
            var_name = "{}".format(option).upper()
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str
            cmake.definitions[var_name] = var_value

        cmake.definitions["PROJECT_VERSION"] = self.version  

        if self.options.shared:
            cmake.definitions["EPROSIMA_ALL_DYN_LINK"] = ""
            cmake.definitions["fastdds_EXPORTS"] = ""


        for option, value in self.options.items():
            add_cmake_option(option, value)


        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):        
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.shared:
            self.cpp_info.defines = ["EPROSIMA_ALL_DYN_LINK"]
