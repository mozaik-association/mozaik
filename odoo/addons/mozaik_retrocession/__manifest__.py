# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Retrocession',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'account',
        'account_auto_installer',
        'mozaik_base',
        'mozaik_structure',
        'mozaik_mandate',
        'mozaik_membership',
        'mozaik_chart_account',
    ],
    'description': """
MOZAIK Retrocession
===================
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/retrocession_security.xml',
        'mandate_actions.xml',
        'structure_view.xml',
        'retrocession_view.xml',
        'mandate_view.xml',
        'wizards/retrocession_factory_wizard.xml',
        'wizards/report_retrocession_wizard.xml',
        'reports/report_payment_request_view.xml',
        'reports/report_payment_certificate_view.xml',
        'data/email_template_data.xml',
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
