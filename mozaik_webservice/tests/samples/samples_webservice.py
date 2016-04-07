#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_webservice, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_webservice is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_webservice is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_webservice.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import sys
import xmlrpclib

URL = 'http://localhost:8069/'

"""
Test mozaik web-service by running this script.
"""
if len(sys.argv) != 3:
    raise Exception(
        'Two arguments are required to launch this sample: '
        '"db {1 | 2 | 3 | 4 | 5 | 6}"')

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
        DBNAME,
        UID,
        PWD,
        OBJECT,
        METHOD,
        'LHERMITTE',
        'Thierry',
        'm',
        'Rue Louis Maréchal 6/2B',
        '4360',
        'Oreye',
        'm',
        01,
        04,
        1985,
        'thierry@gmail.com',
        '0465000000',
        '061412002',
        'Foot, Snowboard',
        False,
        False,
        False)
elif sys.argv[2] == '2':
    METHOD = 'get_login'
    res = sock.execute(
        DBNAME,
        UID,
        PWD,
        OBJECT,
        METHOD,
        'pauline@gmail.com',
        '1949-03-29')
elif sys.argv[2] == '3':
    METHOD = 'membership_request'
    res = sock.execute(
        DBNAME,
        UID,
        PWD,
        OBJECT,
        METHOD,
        'MARCEAU',
        'Sophie',
        'f',
        'Rue Louis Maréhal 6/2B',
        '4360',
        'Oreye',
        'n',
        False,
        False,
        False,
        'vic.beretton@gmail.com',
        False,
        False,
        False,
        'demande newsletter etopia',
        'ETOPIA',
        False,
        False)
elif sys.argv[2] == '4':
    METHOD = 'get_distribution_list'
    res = sock.execute(DBNAME, UID, PWD, OBJECT, METHOD, 1)
elif sys.argv[2] == '5':
    METHOD = 'update_partner_ldap'
    res = sock.execute(DBNAME, UID, PWD, OBJECT, METHOD, 7, 456, 'new name')
elif sys.argv[2] == '6':
    METHOD = 'membership_request'
    res = sock.execute(
        DBNAME,
        UID,
        PWD,
        OBJECT,
        METHOD,
        'Couvent des Ursulines',
        False,
        False,
        'Rue du presbytère 14',
        '4360',
        'Oreye',
        False,
        False,
        False,
        False,
        'soeur.sourire@yeye.np',
        False,
        False,
        False,
        'demande newsletter etopia',
        'ETOPIA',
        'YES',
        'Bières & Fromages')
else:
    raise Exception('Unavailable option')

print res
