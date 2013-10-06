#!/usr/bin/env python
# Copyright 2013 Donald Stufft and individual contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import functools
import glob
import os
import os.path
import subprocess
import sys

from distutils.command.build_clib import build_clib as _build_clib

from setuptools import Distribution, setup


def here(*paths):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *paths))

sodium = functools.partial(here, "src/libsodium/src/libsodium")


sys.path.append(here("src"))


import nacl


def which(name, flags=os.X_OK):  # Taken from twisted
    result = []
    exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
    path = os.environ.get('PATH', None)
    if path is None:
        return []
    for p in os.environ.get('PATH', '').split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, flags):
            result.append(p)
        for e in exts:
            pext = p + e
            if os.access(pext, flags):
                result.append(pext)
    return result


# This hack exists so that we can import nacl here
sys.path += glob.glob("*.egg")

try:
    import nacl.nacl
except ImportError:
    # installing - there is no cffi yet
    ext_modules = []
else:
    # building bdist - cffi is here!
    ext_modules = [nacl.nacl.ffi.verifier.get_extension()]
    ext_modules[0].include_dirs.append(sodium("include"))


class Distribution(Distribution):

    def has_c_libraries(self):
        return True


class build_clib(_build_clib):

    def get_source_files(self):
        files = glob.glob(here("src/libsodium/*"))
        files += glob.glob(here("src/libsodium/*/*"))
        files += glob.glob(here("src/libsodium/*/*/*"))
        files += glob.glob(here("src/libsodium/*/*/*/*"))
        files += glob.glob(here("src/libsodium/*/*/*/*/*"))
        files += glob.glob(here("src/libsodium/*/*/*/*/*/*"))

        return files

    def build_libraries(self, libraries):
        raise Exception("build_libraries")

    def check_library_list(self, libraries):
        raise Exception("check_library_list")

    def get_library_names(self):
        return ["sodium"]

    def run(self):
        # Ensure our temporary build directory exists
        try:
            os.makedirs(os.path.abspath(self.build_temp))
        except IOError:
            pass

        # Locate our configure script
        configure = here("src/libsodium/configure")

        # Run ./configure
        subprocess.check_call(
            [
                configure, "--disable-shared", "--enable-static",
                "--disable-debug", "--disable-dependency-tracking",
                "--prefix", os.path.abspath(self.build_clib),
                "--libdir", os.path.abspath(self.build_clib),
            ],
            cwd=os.path.abspath(self.build_temp),
        )

        # Build the library
        subprocess.check_call(
            ["make", "install"],
            cwd=os.path.abspath(self.build_temp),
        )


setup(
    name=nacl.__title__,
    version=nacl.__version__,

    description=nacl.__summary__,
    long_description=open("README.rst").read(),
    url=nacl.__uri__,
    license=nacl.__license__,

    author=nacl.__author__,
    author_email=nacl.__email__,

    setup_requires=[
        "cffi",
    ],
    install_requires=[
        "cffi",
        "six",
    ],
    extras_require={
        "tests": ["pytest"],
    },
    tests_require=["pytest"],

    package_dir={"": "src"},
    packages=[
        "nacl",
    ],

    ext_package="nacl",
    ext_modules=ext_modules,

    cmdclass={
        "build_clib": build_clib,
    },
    distclass=Distribution,
    zip_safe=False,

    classifiers=[
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ]
)
