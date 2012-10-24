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

"""This module provides the Database interface allowing the user to query the
AR face database.
"""

import os
from bob.db import utils
from .models import *
from .driver import Interface

INFO = Interface()

SQLITE_FILE = INFO.files()[0]

class Database(object):
  """The database class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self):
    # opens a session to the database - keep it open until the end
    self.connect()
    # defines valid entries for various parameters
    self.m_groups  = Client.group_choices
    self.m_purposes = File.purpose_choices
    self.m_genders = Client.gender_choices
    self.m_sessions = File.session_choices
    self.m_expressions = File.expression_choices
    self.m_illuminations = File.illumination_choices
    self.m_occlusions = File.occlusion_choices
    self.m_protocols = Protocol.protocol_choices

  def connect(self):
    """Tries connecting or re-connecting to the database"""
    if not os.path.exists(SQLITE_FILE):
      self.m_session = None
    else:
      self.m_session = utils.session_try_readonly(INFO.type(), SQLITE_FILE)

  def is_valid(self):
    """Returns if a valid session has been opened for reading the database"""
    return self.m_session is not None

  def assert_validity(self):
    """Raise a RuntimeError if the database backend is not available"""
    if not self.is_valid():
      raise RuntimeError, "Database '%s' cannot be found at expected location '%s'. Create it and then try re-connecting using Database.connect()" % (INFO.name(), SQLITE_FILE)


  def __check_validity__(self, elements, description, possibilities, default = None):
    """Checks validity of user input data against a set of valid values"""
    if not elements:
      return default if default else possibilities
    if not isinstance(elements, list) and not isinstance(elements, tuple):
      return self.__check_validity__((elements,), description, possibilities, default)
    for k in elements:
      if k not in possibilities:
        raise RuntimeError, 'Invalid %s "%s". Valid values are %s, or lists/tuples of those' % (description, k, possibilities)
    return elements

  def __check_single__(self, element, description, possibilities, default = None):
    """Checks validity of user input data against a set of valid values"""
    if not element:
      return default
    if isinstance(element,tuple) or isinstance (element,list):
      if len(element) > 1:
        raise RuntimeError, 'For %s, only single elements from %s are allowed' % (description, possibilities)
      element = element[0]
    if element not in possibilities:
      raise RuntimeError, 'The given %s "%s" is not allowed. Please choose one of %s' % (description, element, possibilities)
    return element


  def clients(self, groups=None, genders=None, protocol=None):
    """Returns a list of Client objects for the specific query by the user.

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev', 'eval').
      If not specified, all groups are returned.

    genders
      One of the genders ('m', 'w') of the clients.
      If not specified, clients of all genders are returned.

    protocol
      Ignored since clients are identical for all protocols.

    Returns: A list containing all the Client objects which have the desired properties.
    """

    self.assert_validity()
    groups = self.__check_validity__(groups, "group", self.m_groups)
    genders = self.__check_validity__(genders, "group", self.m_genders)

    query = self.m_session.query(Client)\
                .filter(Client.sgroup.in_(groups))\
                .filter(Client.gender.in_(genders))

    return [client for client in query]


  def client_ids(self, groups=None, genders=None, protocol=None):
    """Returns a list of client ids for the specific query by the user.

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev', 'eval').
      If not specified, all groups are returned.

    genders
      One of the genders ('m', 'w') of the clients.
      If not specified, clients of all genders are returned.

    protocol
      Ignored since clients are identical for all protocols.

    Returns: A list containing all the client ids which have the desired properties.
    """

    self.assert_validity()
    return [client.id for client in self.clients(groups, genders, protocol)]


  # model_ids() and client_ids() functions are identical
  model_ids = client_ids



  def get_client_id_from_file_id(self, file_id):
    """Returns the client_id (real client id) attached to the given file_id

    Keyword Parameters:

    file_id
      The file_id to consider

    Returns: The client_id attached to the given file_id
    """
    self.assert_validity()
    q = self.m_session.query(File)\
            .filter(File.id == file_id)

    assert q.count() == 1
    return q.first().client_id

  def get_client_id_from_model_id(self, model_id):
    """Returns the client_id attached to the given model_id

    Keyword Parameters:

    model_id
      The model id to consider

    Returns: The client_id attached to the given model_id
    """
    # client ids and model ids are identical...
    return model_id



  def objects(self, groups=None, protocol=None, purposes=None, model_ids=None, sessions=None, expressions=None, illuminations=None, occlusions=None, genders=None):
    """Using the specified restrictions, this function returns a list of File objects.

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev', 'eval').

    protocol
      One of the AR protocols ('all', 'expression', 'illumination', 'occlusion', 'occlusion_and_illumination').
      Note: this field is ignored for group 'world'.

    purposes
      One or several purposes for which files should be retrieved ('enrol', 'probe').
      Note: this field is ignored for group 'world'.

    model_ids
      If given (as a list of model id's or a single one), only the files belonging to the specified model id is returned.
      For 'probe' purposes, this field is ignored since probe files are identical for all models.

    sessions
      One or several sessions from ('first', 'second').
      If not specified, objects of all sessions are returned.

    expressions
      One or several expressions from ('neutral', 'smile', 'anger', 'scream').
      If not specified, objects with all expressions are returned.
      Ignored for purpose 'enrol'.

    illuminations
      One or several illuminations from ('front', 'left', 'right', 'all').
      If not specified, objects with all illuminations are returned.
      Ignored for purpose 'enrol'.

    occlusions
      One or several occlusions from ('none', 'sunglasses', 'scarf').
      If not specified, objects with all occlusions are returned.
      Ignored for purpose 'enrol'.

    genders
      One of the genders ('m', 'w') of the clients.
      If not specified, both genders are returned.

    """
    self.assert_validity()

    # check that every parameter is as expected
    groups = self.__check_validity__(groups, "group", self.m_groups)
    self.__check_single__(protocol, "protocol", self.m_protocols)
    purposes = self.__check_validity__(purposes, "purpose", self.m_purposes)
    sessions = self.__check_validity__(sessions, "session", self.m_sessions)
    expressions = self.__check_validity__(expressions, "expression", self.m_expressions)
    illuminations = self.__check_validity__(illuminations, "illumination", self.m_illuminations)
    occlusions = self.__check_validity__(occlusions, "occlusion", self.m_occlusions)
    genders = self.__check_validity__(genders, "gender", self.m_genders)

    # assure that the given model ids are in a tuple
    if isinstance(model_ids, str) or isinstance(model_ids, unicode):
      model_ids = (model_ids,)


    def _filter_types(query):
      return query.filter(File.expression.in_(expressions))\
                  .filter(File.illumination.in_(illuminations))\
                  .filter(File.occlusion.in_(occlusions))\
                  .filter(File.session.in_(sessions))\
                  .filter(Client.gender.in_(genders))
      return query

    queries = []
    probe_queries = []

    if 'world' in groups:
      queries.append(\
        _filter_types(
          self.m_session.query(File).join(Client)\
              .join((Protocol, and_(File.expression == Protocol.expression, File.illumination == Protocol.illumination, File.occlusion == Protocol.occlusion)))\
              .filter(Client.sgroup == 'world')\
              .filter(Protocol.name == protocol)
        )
      )

    if 'dev' in groups or 'eval' in groups:
      t_groups = ('dev',) if not 'eval' in groups else ('eval',) if not 'dev' in groups else ('dev','eval')

      if 'enrol' in purposes:
        queries.append(\
            self.m_session.query(File).join(Client)\
                .filter(Client.sgroup.in_(t_groups))\
                .filter(Client.gender.in_(genders))\
                .filter(File.purpose == 'enrol')\
        )

      if 'probe' in purposes:
        probe_queries.append(\
            _filter_types(
              self.m_session.query(File).join(Client)\
                  .join((Protocol, and_(File.expression == Protocol.expression, File.illumination == Protocol.illumination, File.occlusion == Protocol.occlusion)))\
                  .filter(Client.sgroup.in_(t_groups))\
                  .filter(File.purpose == 'probe')\
                  .filter(Protocol.name == protocol)
            )
        )

    # we have collected all queries, now filter the model ids, if desired
    retval = []

    for query in queries:
      # filter model ids
      if model_ids is not None:
        query = query.filter(Client.id.in_(model_ids))
      retval.extend([file for file in query])

    for query in probe_queries:
      # do not filter model ids
      retval.extend([file for file in query])

    return retval
