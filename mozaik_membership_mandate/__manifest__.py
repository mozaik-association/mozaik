# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mozaik Membership Mandate',
    'description': """
        TODO""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://github.com/OCA/mozaik',
    'depends': [
        'mozaik_membership',
        'mozaik_mandate',
    ],
    'data': [
        'views/abstract_mandate.xml',
        'views/int_mandate.xml',
        'views/ext_mandate.xml',
        'views/sta_mandate.xml',
    ],
    'demo': [
    ],
    "installable": False,
}
