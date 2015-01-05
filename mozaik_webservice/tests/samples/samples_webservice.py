#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import sys
import xmlrpclib

URL = 'http://localhost:8069/'

"""
To test membership web-service by running this script
options
* `1` test membership request
* `2` test get uid
"""
if len(sys.argv) != 3:
    raise Exception('Two arguments are required to launch this sample: "db {1 | 2 | 3}"')

DBNAME = sys.argv[1]
USERNAME = 'ws'
PWD = 'ws%123'

sock_common = xmlrpclib.ServerProxy(URL + 'xmlrpc/common')
UID = sock_common.login(DBNAME, USERNAME, PWD)

sock = xmlrpclib.ServerProxy(URL + 'xmlrpc/object')

OBJECT = 'custom.webservice'
if sys.argv[2] == '1':
    METHOD = 'membership_request'
    res = sock.execute(
        DBNAME, UID, PWD, OBJECT, METHOD,
        'LHERMITTE', 'Thierry', 'm', 'Rue Louis Maréhal 6/2B', '4360', 'Oreye', 'm',
        01, 04, 1985,
        'thierry@gmail.com', '0465000000', '061412002',
        'Foot, Snowboard', False)
elif sys.argv[2] == '2':
    METHOD = 'get_login'
    res = sock.execute(DBNAME, UID, PWD, OBJECT, METHOD, 'pauline@gmail.com', '1949-03-29')
elif sys.argv[2] == '3':
    METHOD = 'membership_request'
    res = sock.execute( \
        DBNAME, UID, PWD, OBJECT, METHOD, \
        'MARCEAU', 'Sophie', 'f', 'Rue Louis Maréhal 6/2B', '4360', 'Oreye', False, \
        False, False, False,
        'vic.beretton@gmail.com', False, False,
        False, 'demande newsletter etopia')
else:
    raise Exception('1, 2 or 3 for available options')

print res
