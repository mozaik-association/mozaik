# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'MOZAIK: Address',
    'description': """
        Module for addresses, postal coordinates and co-residencies""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'base',
        'mozaik_coordinate',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/address_security.xml',
        'data/address_address_data.xml',
        'views/postal_coordinate_view.xml',
        'views/co_residency_view.xml',
        'views/address_address_view.xml',
        'views/address_local_zip_view.xml',
        'views/address_local_street_view.xml',
        'views/coordinate_category_view.xml',
        'views/res_partner_view.xml',
        'wizards/change_main_address.xml',
        'wizards/allow_duplicate_view.xml',
        'wizards/bounce_editor_view.xml',
        'wizards/change_co_residency_address.xml',
        'wizards/print_postal_from_partner_wizard_view.xml',
        'reports/report_res_partner_postal_coordinate_label_view.xml',
        'reports/report_postal_coordinate_label_view.xml',
    ],
    'installable': False,
}
