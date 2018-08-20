# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Phone',
    'summary': """
        Manages phone numbers and phone coordinates.
        It covers three types of phone: fix, mobile and fax.
        Phones are normalized with the external library: phonenumbers""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'base',
        'mail',
        'mozaik_abstract_model',
        'mozaik_coordinate',
    ],
    'data': [
        'security/phone_coordinate.xml',
        'security/phone_phone.xml',
        'views/phone_coordinate.xml',
        'views/phone_phone.xml',
        'views/res_partner.xml',
        'wizards/change_main_phone.xml',
        'wizards/allow_duplicate_view.xml',
        'wizards/failure_editor_view.xml',
        'wizards/change_phone_type.xml',
    ],
    'demo': [
        'demo/phone_phone.xml',
        'demo/phone_coordinate.xml',
    ],
    'external_dependencies': {
        'python': [
            'phonenumbers',
        ],
    },
    'installable': True,
}
