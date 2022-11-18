# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Sample Accounting Localization',
    'version': '14.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    'category': 'Political Association',
    'depends': [
        'mozaik_sample_customization',
        'l10n_mozaik',
    ],
    'description': """
MOZAIK Sample Accounting Localization
=====================================
""",
    'images': [
    ],
    'data': [
        '../mozaik_account/tests/data/account_installer.xml',
        'data/retrocession_validation.xml'
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    "installable": False,
}
