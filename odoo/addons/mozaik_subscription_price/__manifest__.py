# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Subscription prices',
    'summary': """
        Manage subscription prices""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'product',
        'mozaik_structure',
        'mozaik_membership',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/int_instance.xml',
        'views/product_pricelist.xml',
    ],
    'demo': [
        'demo/product_pricelist.xml',
        'demo/product_pricelist_item.xml',
    ],
    "installable": False,
}
