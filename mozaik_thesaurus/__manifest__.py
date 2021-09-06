# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Thesaurus',
    'summary': """
        Implements a light thesaurus for indexation purpose""",
    'version': "14.0.1.0.0",
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://github.com/OCA/mozaik',
    'category': 'Political Association',
    'depends': [
        'base',
        'mail',
        'mozaik_tools',
        'mozaik_abstract_model',
    ],
    'data': [
        'data/thesaurus_data.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/thesaurus.xml',
        'views/thesaurus_term.xml',
        'views/res_partner.xml',
        'views/thesaurus_menu.xml',
    ],
    "installable": True,
}
