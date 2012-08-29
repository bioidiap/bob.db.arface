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

"""Dumps lists of files.
"""

import os
import sys

# Driver API
# ==========

def dumplist(args):
  """Dumps lists of files based on your criteria"""

  from .query import Database
  db = Database()

  r = db.files(
      directory=args.directory,
      extension=args.extension,
      groups=args.group,
      protocol=args.protocol,
      purposes=args.purpose,
      sessions=args.session,
      expressions=args.expression,
      illuminations=args.illumination,
      occlusions=args.occlusion)

  output = sys.stdout
  if args.selftest:
    from bob.db.utils import null
    output = null()

  for f in sorted(r.values()):
    output.write('%s\n' % (f,))

  return 0


def add_command(subparsers):
  """Add specific subcommands that the action "dumplist" can use"""
  
  from argparse import SUPPRESS
  from .create import Client, File, Protocol
  from . import __doc__

  parser = subparsers.add_parser('dumplist', help=dumplist.__doc__)

  parser.add_argument('-d', '--directory', help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
  parser.add_argument('-e', '--extension', help="if given, this extension will be appended to every entry returned (defaults to '%(default)s')")
  parser.add_argument('-g', '--group', help="if given, this value will limit the output files to those belonging to a particular group. (defaults to '%(default)s')", choices = Client.s_groups)
  parser.add_argument('-p', '--protocol', default = 'all', help="limits the dump to a particular subset of the data that corresponds to the given protocol (defaults to '%(default)s')", choices = Protocol.s_protocols)
  parser.add_argument('-u', '--purpose', help="if given, this value will limit the output files to those designed for the given purposes.", choices=File.s_purposes)
  parser.add_argument('-s', '--session', help="if given, this value will limit the output files to those designed for the given session.", choices=File.s_sessions)
  parser.add_argument('-w', '--gender', help="if given, this value will limit the output files to those designed for the given gender.", choices=Client.s_genders)
  parser.add_argument('-x', '--expression', help="if given, this value will limit the output files to those designed for the given expression.", choices=File.s_expressions)
  parser.add_argument('-i', '--illumination', help="if given, this value will limit the output files to those designed for the given illumination.", choices=File.s_illuminations)
  parser.add_argument('-o', '--occlusion', help="if given, this value will limit the output files to those designed for the given illumination.", choices=File.s_occlusions)
  parser.add_argument('--self-test', dest="selftest", action='store_true', help=SUPPRESS)

  parser.set_defaults(func=dumplist) #action

