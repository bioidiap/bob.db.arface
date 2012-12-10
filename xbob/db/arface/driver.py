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
import argparse

from bob.db.driver import Interface as BaseInterface

def dumplist(args):
  """Dumps lists of files based on your criteria"""

  from .query import Database
  db = Database()

  r = db.objects(
      groups=args.group,
      protocol=args.protocol,
      purposes=args.purpose,
      model_ids=args.client,
      sessions=args.session,
      expressions=args.expression,
      illuminations=args.illumination,
      occlusions=args.occlusion)

  output = sys.stdout
  if args.selftest:
    from bob.db.utils import null
    output = null()

  for f in r:
    output.write('%s\n' % (f.make_path(args.directory, args.extension),))

  return 0


def checkfiles(args):
  """Checks existence of files based on your criteria"""

  from .query import Database
  db = Database()

  r = db.objects()

  # go through all files, check if they are available on the filesystem
  good = {}
  bad = {}
  for f in r:
    if os.path.exists(f.make_path(args.directory,args.extension)): good[f.id] = f
    else: bad[f.id] = f

  # report
  output = sys.stdout
  if args.selftest:
    from bob.db.utils import null
    output = null()

  if bad:
    for id, f in bad.items():
      output.write('Cannot find file "%s"\n' % f.make_path(args.directory,args.extension))
    output.write('%d files (out of %d) were not found at "%s"\n' % \
        (len(bad), len(r), args.directory))

  return 0


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

    # the "create" action
    from .create import add_command as create_command
    create_command(subparsers)

    from .query import Database
    from .models import Client, File, Protocol
    db = Database()

    # the "dumplist" action
    parser = subparsers.add_parser('dumplist', help=dumplist.__doc__)
    parser.add_argument('-d', '--directory', help="if given, this path will be prepended to every entry returned.")
    parser.add_argument('-e', '--extension', help="if given, this extension will be appended to every entry returned.")
    parser.add_argument('-g', '--group', help="if given, this value will limit the output files to those belonging to a particular group.", choices = Client.group_choices)
    parser.add_argument('-p', '--protocol', default = 'all', help="limits the dump to a particular subset of the data that corresponds to the given protocol.", choices = Protocol.protocol_choices)
    parser.add_argument('-u', '--purpose', help="if given, this value will limit the output files to those designed for the given purposes.", choices=File.purpose_choices)
    parser.add_argument('-C', '--client', help="if given, this value will limit the output files to those designed for the given purposes.", choices=db.client_ids() if db.is_valid() else ())
    parser.add_argument('-s', '--session', help="if given, this value will limit the output files to those designed for the given session.", choices=File.session_choices)
    parser.add_argument('-w', '--gender', help="if given, this value will limit the output files to those designed for the given gender.", choices=Client.gender_choices)
    parser.add_argument('-x', '--expression', help="if given, this value will limit the output files to those designed for the given expression.", choices=File.expression_choices)
    parser.add_argument('-i', '--illumination', help="if given, this value will limit the output files to those designed for the given illumination.", choices=File.illumination_choices)
    parser.add_argument('-o', '--occlusion', help="if given, this value will limit the output files to those designed for the given occlusion.", choices=File.occlusion_choices)
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=dumplist) #action

    # the "checkfiles" action
    parser = subparsers.add_parser('checkfiles', help=checkfiles.__doc__)
    parser.add_argument('-d', '--directory', help="if given, this path will be prepended to every entry returned.")
    parser.add_argument('-e', '--extension', help="if given, this extension will be appended to every entry returned.")
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=checkfiles) #action

