# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Account',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'product',
        'account',
        'account_accountant',
        'account_cancel',
        'account_auto_installer',
        'mozaik_person',
        'mozaik_mandate',
        'mozaik_chart_account',
        'mozaik_membership',
        'mozaik_retrocession',
    ],
    'description': """
MOZAIK Account
==============
Manage accounting features
""",
    'images': [
    ],
    'data': [
        'data/product_data.xml',
        'security/account_security.xml',
        'account_view.xml',
        'views/product_view.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'installable': False,
}
