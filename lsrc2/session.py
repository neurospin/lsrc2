# -*- coding: utf-8 -*-
# Copyright (c) 2016 CEA
#
# This software is governed by the CeCILL-C license under French law and
# abiding by the rules of distribution of free software. You can use,
# modify and/ or redistribute the software under the terms of the CeCILL-C
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty and the software's author, the holder of the
# economic rights, and the successive licensors have only limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading, using, modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean that it is complicated to manipulate, and that also
# therefore means that it is reserved for developers and experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and, more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL-C license and that you accept its terms.

import requests
import json
import base64
import logging


class Session(object):
    """ Session to remote LimeSurvey_ servers.
    
    Persists authentication and other settings while accessing LimeSurvey_
    servers using the `RemoteControl 2 API`_.

    Basic Usage::

      >>> import lsrc2
      >>> s = lsrc2.Session('https://lsdemo.limequery.com/admin/remotecontrol', 'limedemo', 'demo')
      >>> surveys, error = s.surveys()
      >>> type(surveys), type(error)
      (list, NoneType)

    Or as a context manager::

      >>> with lsrc2.Session('https://lsdemo.limequery.com/admin/remotecontrol', 'limedemo', 'demo') as s:
      >>>     surveys, error = s.surveys()
      >>> type(surveys), type(error)
      (list, NoneType)

    For now Session is limited to JSON-RPC requests and provides no way
    to switch to XML-RPC requests as the documentation reads:
        We recommend in general to use JSON-RPC because it is well tested
        and has a much smaller footprint than XML-RPC.

    Parameters
    ----------
    url : str
    username : str
    password : str

    Attributes
    ----------
    url : str
        Base LSRC2 URL.
    session : requests.Session
        Requests session instance.
    key : str
        LSRC2 session key.

.. _LimeSurvey: https://www.limesurvey.org
.. _RemoteControl 2 API: https://manual.limesurvey.org/RemoteControl_2_API

    """
    __attrs__ = ['url', 'session', 'key']

    __request_id = 0

    def __init__(self, url, username, password):
        self.url = url
        # start a Requests session
        self.session = requests.Session()
        # Keep-alive is 100% automatic in Requests, thanks to urllib3
        self.session.headers.update({'content-type': 'application/json'})
        # start a LimeSurvey RemoteControl 2 session
        self.key = self._get_session_key(username, password)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
        return False  # re-raises the exception

    def close(self):
        """Release LimeSurvey session key, then close Requests session"""
        self._release_session_key(self.key)
        self.key = None
        self.session.close()

    @staticmethod
    def _generate_request_id():
        Session.__request_id += 1
        return Session.__request_id

    @staticmethod
    def _request(method, params):
        return {
            'jsonrpc': '2.0',
            'id': Session._generate_request_id(),
            'method': method,
            'params': params,
        }

    def _post(self, request):
        logging.debug('JSON-RPC request: {0}'.format(request))
        assert 'method' in request and 'params' in request and 'id' in request
        response = self.session.post(self.url, data=json.dumps(request))
        response = response.json()
        logging.debug('JSON-RPC response: {0}'.format(response))
        assert response['id'] == request['id']
        result = response['result']
        error = response['error']
        if error:
            logging.error('LSRC2 error: {0}'.format(error))
        return result, error

    def _get_session_key(self, username, password):
        """Call `get_session_key`_

        Parameters
        ----------
        username : str
        password : str

        Returns
        -------
        str
            Session key, None in case of error.

        .. _get_session_key: http://api.limesurvey.org/classes/remotecontrol_handle.html#method_get_session_key

        """
        request = self._request('get_session_key', [username, password])
        response, error = self._post(request)

        # fix non-sensical LSRC2 error handling
        # completely at odds with JSON-RPC error handling
        try:
            status = response['status']
        except (TypeError, KeyError):
            if error is not None:
                logger.error('LSRC2 failed to create a session key')
                response = None
            else:
                logging.info('LSRC2 new session key: {0}'.format(response))
        else:
            logger.error(status)
            error = {
                'code': -32099,  # implementation-defined error in JSON-RPC
                'message': status,
            }
            response = None

        return response

    def _release_session_key(self, key):
        """Call `release_session_key`_

        Parameters
        ----------
        key : str

        .. _release_session_key: http://api.limesurvey.org/classes/remotecontrol_handle.html#method_release_session_key

        """
        request = self._request('release_session_key', [key])
        logging.info('LSRC2 release session key: {0}'.format(key))
        response, error = self._post(request)  # returns ('OK', None) even if bogus key

    def surveys(self):
        """Call `list_surveys`_

        If user is admin, returns all surveys, otherwise only those
        belonging to the user.

        Returns
        -------
            response : array
                Array of IDs and info.
            error : dict
                Dictionary contains `code` and `message`.

        .. _list_surveys: http://api.limesurvey.org/classes/remotecontrol_handle.html#method_list_surveys

        """
        request = self._request('list_surveys', [self.key])
        return self._post(request)

    def participants(self, survey, start=0, limit=500, unused=False, attributes=False):
        request = self._request('list_participants',
                                [self.key, survey, start, limit, unused, attributes])
        responses, error = self._post(request)

        # fix non-sensical LSRC2 error handling
        # completely at odds with JSON-RPC error handling
        try:
            status = responses['status']
        except (TypeError, KeyError):
            pass
        else:
            # LSRC2 returns errors as a dict with a 'status' attribute
            if status == 'No Tokens found':
                # When a survey is empty, LSRC2 also returns a dict:
                # {"status": "No Tokens found"}
                if error is not None:
                    logger.error('JSON-RPC error report does not match "status"')
                    error = None
            else:
                error = {
                    'code': -32099,  # implementation-defined error in JSON-RPC
                    'message': status,
                }
            responses = []

        return responses, error

    def participant_properties(self, survey, participant, attributes):
        request = self._request('get_participant_properties',
                                [self.key, survey, participant, attributes])
        return self._post(request)

    def delete_participants(self, survey, tokens):
        request = self._request('delete_participants',
                                [self.key, survey, tokens])
        responses, error = self._post(request)

        # When a survey is empty, LimeSurvey returns this dict:
        #    {"status": "No Data, could not get max id."}
        if type(responses) is dict:
            if 'status' in responses:
                error = {
                    'code': -32500,  # application error in XML-RPC
                    'message': responses['status'],
                }
            else:
                message = 'JSON-RPC function "export_responses" returned a dictionnary, expected a Base64-encoded string'
                logger.error(message)
                error = {
                    'code': -32500,  # application error in XML-RPC
                    'message': message,
                }
            responses = []

        return responses, error


def session():
    """
    Returns a :class:`Session` for context-management.

    Returns
    -------
        session : Session

    """
    return Session()
