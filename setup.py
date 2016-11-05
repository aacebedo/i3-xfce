#!/usr/bin/env python2
#
# i3-xfce
# Copyright (c) 2015, Alexandre ACEBEDO, All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.
#
"""
Setup script for i3-xfce
"""
import sys
import os
from platform import python_version
import distutils
try:
  from setuptools import setup, find_packages
except ImportError:
  sys.exit("setuptools package is missing")
try:
  import versioneer
except ImportError:
  sys.exit("versioneer package is missing")

def execute_setup():
  """
  Setup function
  """
  if sys.version_info < (2, 0) or sys.version_info >= (3, 0):
    sys.exit("i3-xfce only supports python2. Please run setup.py with python2.")

  data_files = []

  for dname, dirs, _ in os.walk("resources"):
    for fname in dirs:
      for cur_file in os.listdir(os.path.join(dname, fname)):
        if os.path.isfile(os.path.join(dname, fname, cur_file)):
          real_path = os.path.relpath((os.path.join(dname, fname, cur_file)), "resources")
          data_files.append((os.path.join("i3xfce", "resources",
                                          os.path.dirname(str(real_path))),
                             [os.path.join("resources", str(real_path))]))

  requirements = [i.strip() for i in open("requirements.txt").readlines()]

  setup(
      name="i3-xfce",
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      packages=find_packages("src"),
      package_dir={'':'src'},
      data_files=data_files,
      install_requires=requirements,
      author="Alexandre ACEBEDO",
      author_email="Alexandre ACEBEDO",
      description="I3 installer for xfce4",
      license="LGPLv3",
      keywords="i3 xfce",
      url="http://github.com/aacebedo/i3-xfce",
      entry_points={'console_scripts':
                    ['i3-xfce = i3xfce.core:main']}
      )

if __name__ == "__main__":
  execute_setup()
