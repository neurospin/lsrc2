Python LimeSurvey
=================

The Python LimeSurvey module encapuslates the JSON-RPC LimeSurvey_ `Remote
Control 2 API`_ *(LSRC2)* in a straightforward Python API. Now your Python
scripts will easily interact with remote LimeSurvey_ servers::

    >>> s = lsrc2.LimeSurveySession(base_url, username, password)
    >>> surveys, error = s.surveys()

.. _LimeSurvey: https://www.limesurvey.org
.. _Remote Control 2 API: https://manual.limesurvey.org/RemoteControl_2_API


User Guide
==========

TODO
