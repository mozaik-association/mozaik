# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mozaik: Account',
    'summary': """
        Manage membership and donation reconciliation""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'product',
        'account',
        'mozaik_involvement',
        'mozaik_membership',
        'l10n_generic_coa',
    ],
    'data': [
        'data/product_product.xml',
        'views/account_bank_statement.xml',
        'views/product_template.xml',
        'views/res_partner.xml',
        'views/membership_line.xml',
    ],
    'demo': [
        'demo/product_product.xml',
        'demo/ir_property.xml'
    ],
    'installable': True,
}
