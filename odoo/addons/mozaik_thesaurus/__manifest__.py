# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Thesaurus',
    'summary': """
        Implements a light thesaurus for indexation purpose""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'base',
        'contacts',
        'mozaik_abstract_model',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'security/thesaurus_term_rule.xml',
        'views/thesaurus.xml',
        'views/thesaurus_term.xml',
        'views/thesaurus_menu.xml',
        'views/res_partner_view.xml',
        'data/thesaurus_data.xml',
    ],
    'installable': True,
}
