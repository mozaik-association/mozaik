# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Base Abstract Model',
    'description': """
        Abstract model for mozaik models""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'base',
        'mail',
        'disable_tracking_installation',
        'inherit_abstract_view',
    ],
    'data': [
        'security/res_groups.xml',
    ],
}
