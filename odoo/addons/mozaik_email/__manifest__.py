# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Email',
    'summary': """
        Manage email and email coordinates.""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'mozaik_coordinate',
    ],
    'data': [
        'data/email_coordinate.xml',
        'views/email_coordinate.xml',
        'views/coordinate_category.xml',
        'views/res_partner.xml',
        'views/res_users.xml',
        'wizards/change_main_email.xml',
        'wizards/allow_duplicate_wizard.xml',
        'wizards/failure_editor.xml',
        'security/email_coordinate.xml',
    ],
    'demo': [
        'demo/email_coordinate.xml',
    ],
    'installable': True,
}
