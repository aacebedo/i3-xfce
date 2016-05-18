#!/usr/bin/env python3
#
# cfdnsupdater
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
import pathlib
import argparse
import platform
import os
import distutils
try:
  from setuptools import setup, find_packages
except Exception as e:
  sys.exit("setuptools for python3 is missing")


def process_setup():
    """
    Setup function
    """
    if sys.version_info < (3,0):
        sys.exit("i3-xfce only supports python3. Please run setup.py with python3.")
  
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--prefix", type=str)
    args, _ = parser.parse_known_args(sys.argv[1:])

    prefix = sys.exec_prefix
    if args.prefix != None:
        prefix = args.prefix

    data_files = []
    
    if platform.system() == "Linux":
        for dname, dirs, _ in os.walk("resources"):
            for fname in dirs:                
                for f in os.listdir(os.path.join(dname,fname)):
                  if os.path.isfile(os.path.join(dname,fname, f)):
                    real_path = pathlib.Path(os.path.join(dname,fname,f)).relative_to("resources")                    
                    data_files.append((os.path.dirname(str(real_path)),[os.path.join("resources",str(real_path))]))
    
    res = distutils.spawn.find_executable("ansible")
    if res is None:
      print("Installation is not possible (ansible not found). Please install ansible before i3-xfce.")
    else:
      setup(
          name="i3-xfce",
          version="0.5.0",
          packages=find_packages("src"),
          package_dir ={'':'src'},
          data_files=data_files,
          install_requires=['argcomplete>=1.0.0','argparse>=1.0.0', 'pyyaml>=3.10', 'progressbar2>=2.0.0'],
          author="Alexandre ACEBEDO",
          author_email="Alexandre ACEBEDO",
          description="I3 installer for xfce4",
          license="LGPLv3",
          keywords="cloudflare dns",
          url="http://github.com/aacebedo/i3-xfce",
          entry_points={'console_scripts':
                        ['i3-xfce = i3xfce.__main__:CmdLine.main']}
      )
      
if __name__ == "__main__":
    process_setup()