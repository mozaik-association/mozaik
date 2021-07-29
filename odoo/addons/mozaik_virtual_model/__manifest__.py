# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Virtual models',
    'summary': """
        Manage virtual models for distribution lists filters""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'base',
        'mozaik_abstract_model',
        'mozaik_structure',
        'mozaik_membership',
        'mozaik_thesaurus',
        'mozaik_involvement',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    "installable": False,
}
