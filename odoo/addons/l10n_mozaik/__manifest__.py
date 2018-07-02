# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Chart of account',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Localization/Account Charts',
    'depends': [
        'account',
    ],
    'description': """
l10n MOZAIK
===========
This is the base module to manage the generic accounting chart for the
application
""",
    'images': [
    ],
    'data': [
        'data/account_template.xml',
        'data/account_chart_template.xml',
        'data/account_installer.xml',
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
