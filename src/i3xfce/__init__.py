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
This module contains the i3-xfce application
"""
import sys
from ._version import get_versions

if sys.version_info < (2, 0) or sys.version_info >= (3, 0):
  sys.exit("i3-xfce only supports python2. Please run setup.py with python2.")

__version__ = get_versions()['version']
del get_versions

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
