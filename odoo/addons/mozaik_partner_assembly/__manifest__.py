# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Partner Assembly',
    'summary': """
        Add a field 'is_assembly' to a partner""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'base',
    ],
    'data': [
        'views/res_partner.xml',
    ],
    'installable': True,
}
