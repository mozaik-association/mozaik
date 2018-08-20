# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Partner Usual Firstname',
    'summary': """
        Allow to specify usual firstname and lastname on
        non-company partners""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'depends': [
        'base',
        'mail',
        'partner_firstname',
    ],
    'data': [
        'views/res_partner.xml',
    ],
    'installable': True,
}
