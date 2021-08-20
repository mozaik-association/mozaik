# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Mozaik: Duplicate',
    'summary': """
        Abstract model wizard to detect, repair and allow duplicates""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://github.com/OCA/mozaik',
    'category': 'Political Association',
    'depends': [
        'mail',
        'mozaik_abstract_model',
    ],
    'data': [
        'wizards/allow_duplicate_view.xml',
    ],
    "installable": False,
}
