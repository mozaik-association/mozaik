# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Account',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'product',
        'account',
        'mozaik_involvement',
        'mozaik_membership',
        'l10n_generic_coa',
    ],
    'description': """
MOZAIK Account
==============
Manage accounting features
""",
    'images': [
    ],
    'data': [
        'data/product_product.xml',
        'views/account_bank_statement.xml',
        'views/product_template.xml',
    ],
    'demo': [
        'demo/product_product.xml',
        'demo/ir_property.xml'
    ],
    'license': 'AGPL-3',
    'installable': True,
}
