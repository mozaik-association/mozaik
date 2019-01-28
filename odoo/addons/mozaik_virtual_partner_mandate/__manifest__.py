# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mozaik Virtual Partner Mandate',
    'description': """
        Virtual model for mandates""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'depends': [
        'mozaik_communication',
        'mozaik_mandate',
    ],
    'data': [
        'views/virtual_partner_mandate.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
}
