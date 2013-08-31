#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""A few checks at the AR Face database.
"""

import os, sys
import unittest
import xbob.db.arface

class ARfaceDatabaseTest(unittest.TestCase):
  """Performs various tests on the AR Face database."""

  def test01_clients(self):
    db = xbob.db.arface.Database()

    # test that the expected number of clients is returned
    self.assertEqual(len(db.client_ids()), 136)
    self.assertEqual(len(db.client_ids(genders='m')), 76)
    self.assertEqual(len(db.client_ids(genders='w')), 60)
    self.assertEqual(len(db.client_ids(groups='world')), 50)
    self.assertEqual(len(db.client_ids(groups='dev')), 43)
    self.assertEqual(len(db.client_ids(groups='eval')), 43)
    self.assertEqual(len(db.client_ids(groups='dev', genders='m')), 24)
    self.assertEqual(len(db.client_ids(groups='eval', genders='m')), 24)

    self.assertEqual(db.model_ids(), [client.id for client in db.clients()])


  def test02_files(self):
    db = xbob.db.arface.Database()

    # test that the files() function returns reasonable numbers of files
    self.assertEqual(len(db.objects(protocol='all')), 3312)

    # number of world files for the two genders
    self.assertEqual(len(db.objects(groups='world', protocol='all')), 1076)
    self.assertEqual(len(db.objects(groups='world', genders='m', protocol='all')), 583)
    self.assertEqual(len(db.objects(groups='world', genders='w', protocol='all')), 493)

    # number of world files are identical for all protocols
    self.assertEqual(len(db.objects(groups='world', protocol='expression')), 1076)
    self.assertEqual(len(db.objects(groups='world', protocol='illumination')), 1076)
    self.assertEqual(len(db.objects(groups='world', protocol='occlusion')), 1076)
    self.assertEqual(len(db.objects(groups='world', protocol='occlusion_and_illumination')), 1076)

    for g in ['dev', 'eval']:
      # assert that each dev and eval client has 26 files
      model_ids = db.model_ids(groups=g)
      self.assertEqual(len(db.objects(groups=g, protocol='all')), 26 * len(model_ids))
      for protocol in db.m_protocols:
        self.assertEqual(len(db.objects(groups=g, purposes='enrol', protocol=protocol)), 2 * len(model_ids))
      for model_id in model_ids:
        # two enrol files for all protocols
        for protocol in db.m_protocols:
          self.assertEqual(len(db.objects(groups=g, model_ids = model_id, purposes='enrol', protocol=protocol)), 2)

        # 24 probe files for the (default) 'all' protocol
        self.assertEqual(len(db.objects(groups=g, model_ids = model_id, purposes='probe', protocol='all')), 24 * len(model_ids))
        # 6 probe files for the 'expression' protocol
        self.assertEqual(len(db.objects(groups=g, model_ids = model_id, purposes='probe', protocol='expression')), 6 * len(model_ids))
        # 6 probe files for the 'illumination' protocol
        self.assertEqual(len(db.objects(groups=g, model_ids = model_id, purposes='probe', protocol='illumination')), 6 * len(model_ids))
        # 4 probe files for the 'occlusion' protocol
        self.assertEqual(len(db.objects(groups=g, model_ids = model_id, purposes='probe', protocol='occlusion')), 4 * len(model_ids))
        # and finally 8 probe files for the 'occlusion_and_illumination' protocol
        self.assertEqual(len(db.objects(groups=g, model_ids = model_id, purposes='probe', protocol='occlusion_and_illumination')), 8 * len(model_ids))


  def test03_annotations(self):
    # Tests that for all files the annotated eye positions exist and are in correct order
    db = xbob.db.arface.Database()

    for f in db.objects():
      annotations = db.annotations(f.id)
      self.assertTrue(annotations is not None)
      self.assertEqual(len(annotations), 2)
      self.assertTrue('leye' in annotations)
      self.assertTrue('reye' in annotations)
      self.assertEqual(len(annotations['reye']), 2)
      self.assertEqual(len(annotations['leye']), 2)
      # assert that the eye positions are not exchanged
      self.assertTrue(annotations['leye'][1] > annotations['reye'][1])


  def test04_driver_api(self):

    from bob.db.script.dbmanage import main
    self.assertEqual(main('arface dumplist --self-test'.split()), 0)
    self.assertEqual(main('arface dumplist --group=dev --protocol=expression --purpose=probe --session=first --client=m-001 --gender=m --expression=anger --illumination=front --occlusion=none --self-test'.split()), 0)
    self.assertEqual(main('arface checkfiles --self-test'.split()), 0)
    # actually, path's and id's are identical in ARface. Nonetheless, test the API:
    self.assertEqual(main('arface reverse m-038-20 --self-test'.split()), 0)
    self.assertEqual(main('arface path m-038-20 --self-test'.split()), 0)

