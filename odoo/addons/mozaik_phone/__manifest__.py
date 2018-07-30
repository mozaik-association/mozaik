# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'MOZAIK: Phone',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'base',
        'mail',
        'mozaik_abstract_model',
        'mozaik_coordinate',
    ],
    'description': """
MOZAIK Phone
============
This module manages phone numbers and phone coordinates.
It covers three types of phone: fix, mobile and fax.
Numbers are normalized regarding the external python library: phonenumbers
""",
    'data': [
        'security/phone_coordinate.xml',
        'security/phone_phone.xml',
        'views/phone_coordinate.xml',
        'views/phone_phone.xml',
        'views/res_partner.xml',
        'data/ir_config_parameter.xml',
        'data/mail_message_subtype.xml',
        'wizards/change_main_phone.xml',
        'wizards/allow_duplicate_view.xml',
        'wizards/failure_editor_view.xml',
        'wizards/change_phone_type.xml',
    ],
    'demo': [
        'demo/phone_phone.xml',
        'demo/phone_coordinate.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'external_dependencies': {
        'python': [
            'phonenumbers',
        ],
    },
}
