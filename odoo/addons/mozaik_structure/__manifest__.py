# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Structure',
    'summary': """
        Module to manage state and political hierarchy""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'base',
        'mozaik_abstract_model',
    ],
    'data': [
        'data/structure_data.xml',
        'security/structure_security.xml',
        'security/ir.model.access.csv',
        'views/abstract_power_level.xml',
        'views/abstract_assembly_category.xml',
        'views/abstract_instance.xml',
        'views/abstract_assembly.xml',
        'views/sta_instance.xml',
        'views/sta_assembly_category.xml',
        'views/int_assembly.xml',
        'views/int_assembly_category.xml',
        'views/ext_assembly.xml',
        'views/legislature.xml',
        'views/electoral_district.xml',
        'views/sta_assembly.xml',
        'views/int_instance.xml',
        'views/sta_power_level.xml',
        'views/int_power_level.xml',
        'views/ext_assembly_category.xml',
        'views/structure_menu.xml',
    ],
    'installable': False,
}
