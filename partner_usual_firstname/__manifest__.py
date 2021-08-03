# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Partner Usual Firstname',
    'summary': """
        Allow to specify usual firstname and lastname on
        non-company partners""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://github.com/OCA/mozaik',
    'depends': [
        'base',
        'partner_firstname',
    ],
    'data': [
        'views/res_partner.xml',
    ],
    "installable": False,
}
