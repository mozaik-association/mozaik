# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Coordinate',
    'summary': """
        Manage coordinates categories: private, professional, ...
        Provide an abstract model and wizard for all kinds of coordinates""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'base',
        'contacts',
        'mail',
        'mozaik_abstract_model',
        'mozaik_duplicate',
    ],
    'data': [
        'security/res_groups.xml',
        'security/coordinate_category.xml',
        'views/res_partner.xml',
        'views/abstract_coordinate.xml',
        'views/coordinate_category.xml',
        'wizards/failure_editor.xml',
        'wizards/change_main_coordinate.xml',
    ],
    'demo': [
        'demo/res_partner.xml',
    ],
    "installable": False,
}
