# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'MOZAIK: Address',
    'summary': """
        Module for addresses, postal coordinates and co-residencies""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'base',
        'mail',
        'contacts',
        'base_address_city',
        'mozaik_tools',
        'mozaik_coordinate',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/address_security.xml',
        'views/postal_coordinate.xml',
        'views/co_residency.xml',
        'views/address_address.xml',
        'views/res_city.xml',
        'views/coordinate_category.xml',
        'views/res_partner.xml',
        'wizards/change_main_address.xml',
        'wizards/allow_duplicate_wizard.xml',
        'wizards/failure_editor.xml',
        'wizards/change_co_residency_address.xml',
    ],
    'demo': [
        'demo/res_city.xml',
        'demo/address_address.xml',
        'demo/postal_coordinate.xml',
    ],
    'installable': True,
}
