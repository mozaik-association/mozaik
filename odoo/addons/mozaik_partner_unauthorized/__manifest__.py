# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Unauthorized Partner',
    'summary': """
        Add a boolean 'unauthorized' on partners.
        It is computed from all its unauthorized main coordinates.""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'base',
        'mozaik_coordinate',
        'mozaik_email',
        'mozaik_address',
        'mozaik_phone',
    ],
    'data': [
        'views/res_partner.xml',
    ],
    'auto_install': True,
    "installable": False,
}
