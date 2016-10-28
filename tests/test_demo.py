#! /usr/bin/env python
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

import lsrc2

LS_DEMO_URL = 'https://lsdemo.limequery.com/admin/remotecontrol'
LS_DEMO_USERNAME = 'limedemo'
LS_DEMO_PASSWORD = 'demo'


def test1(base_url, username, password):
    with lsrc2.Session(base_url, username, password) as session:
        surveys, error = session.surveys()
        for survey in surveys:
            title = survey['surveyls_title']
            sid = survey['sid']
            print(u'▶ {} ▶ {}'.format(sid, title))
            participants, error = session.participants(sid)


def test2(base_url, username, password):
    session = lsrc2.Session(base_url, username, password)
    surveys, error = session.surveys()
    for survey in surveys:
        title = survey['surveyls_title']
        sid = survey['sid']
        print(u'▶ {} ▶ {}'.format(sid, title))
    session.close()


def main():
    test1(LS_DEMO_URL, LS_DEMO_USERNAME, LS_DEMO_PASSWORD)
    test2(LS_DEMO_URL, LS_DEMO_USERNAME, LS_DEMO_PASSWORD)


if __name__ == "__main__":
    main()
