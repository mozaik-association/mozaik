# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Mozaik: Duplicate',
    'description': """
        Abstract model wizard to detect, repair and allow duplicates""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'base_suspend_security',
        'mozaik_base',
        'mozaik_abstract_model',
    ],
    'data': [
        'wizards/allow_duplicate_view.xml',
    ],
    'installable': True,
}
