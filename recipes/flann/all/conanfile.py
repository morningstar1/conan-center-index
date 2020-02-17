import os

from conans import ConanFile, CMake, tools


class LibFlannConan(ConanFile):
    name = "flann"
    description = "Fast Library for Approximate Nearest Neighbors"
    topics = "conan", "flann"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.cs.ubc.ca/research/flann/"
    license = "BSD-3-Clause"
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_hdf5": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_hdf5": True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def requirements(self):
        if self.options.with_hdf5:
            self.requires("hdf5/1.10.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)

        # TODO: check options
        # Only build the C++ libraries
        cmake.definitions["BUILD_DOC"] = "OFF"
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.definitions["BUILD_C_BINDINGS"] = "OFF"
        cmake.definitions["BUILD_MATLAB_BINDINGS"] = "OFF"
        cmake.definitions["BUILD_PYTHON_BINDINGS"] = "OFF"

        # Workaround issue with flann_cpp
        if self.settings.os == "Windows" and self.options.shared:
            cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

        # Remove pkg-config files
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        # Remove MS runtime files (KB-H021)
        for file_to_remove in ["concrt140.dll", "msvcp140.dll", "vcruntime140.dll"]:
            path = os.path.join(self.package_folder, "bin", file_to_remove)
            if os.path.isfile(path):
                os.remove(path)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "FLANN"
        self.cpp_info.names["cmake_find_package_multi"] = "FLANN"
        self.cpp_info.libs = tools.collect_libs(self) # TODO
