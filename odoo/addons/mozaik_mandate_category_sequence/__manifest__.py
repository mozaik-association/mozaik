# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mozaik Mandate Category Sequence',
    'description': """
        Add sequence on mandate category""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'depends': [
        "mozaik_mandate",
    ],
    'data': [
        'views/generic_mandate.xml',
        'views/mandate_category.xml',
    ],
    'demo': [
    ],
    "installable": False,
}
