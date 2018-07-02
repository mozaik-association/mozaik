# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_help',
        'mozaik_mobile',
        'mozaik_portal',
        'mozaik_person',
        'mozaik_involvement_followup',
        'mozaik_automatic_supporter',
        'mozaik_chart_account',
        'mozaik_retrocession',
        'mozaik_account',
        'mozaik_communication',
        'connector_support',
    ],
    'description': """
MOZAIK
======
Loads all applicative modules
""",
    'images': [
    ],
    'data': [
        'security/security.xml',
        'data/res_users_data.xml',
        'views/mail_followers.xml',
    ],
    'qweb': [
    ],
    'demo': [
        'demo/res_users_demo.xml',
    ],
    'license': 'AGPL-3',
    'installable': False,
}
