Python LimeSurvey
=================

The Python `lsrc2` module encapuslates the JSON-RPC LimeSurvey_
`RemoteControl 2 API`_ *(LSRC2)* in a straightforward Python API.
Now your Python scripts will easily interact with remote LimeSurvey_ servers::

    >>> s = lsrc2.Session(base_url, username, password)
    >>> surveys, error = s.surveys()

.. _LimeSurvey: https://www.limesurvey.org
.. _RemoteControl 2 API: https://manual.limesurvey.org/RemoteControl_2_API


User Guide
==========

TODO
