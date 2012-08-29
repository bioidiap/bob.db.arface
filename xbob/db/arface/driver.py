#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch> 
# @date:   Wed Jul  4 14:12:51 CEST 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Commands this database can respond to.
"""

import os
import sys

from bob.db.driver import Interface as BaseInterface

class Interface(BaseInterface):
   
  def name(self):
    return 'arface'
  
  def version(self):
    import pkg_resources  # part of setuptools
    return pkg_resources.require('xbob.db.%s' % self.name())[0].version
  
  def files(self):

    from pkg_resources import resource_filename
    raw_files = ('db.sql3',)
    return [resource_filename(__name__, k) for k in raw_files]

  def type(self):
    return 'sqlite'

  def add_commands(self, parser):

    from . import __doc__ as docs
    
    subparsers = self.setup_parser(parser,
      "AR Face database", docs)

    # example: get the "create" action from a submodule
    from .create import add_command as create_command
    create_command(subparsers)

    # example: get the "dumplist" action from a submodule
    from .dumplist import add_command as dumplist_command
    dumplist_command(subparsers)

    # example: get the "checkfiles" action from a submodule
    from .checkfiles import add_command as checkfiles_command
    checkfiles_command(subparsers)

