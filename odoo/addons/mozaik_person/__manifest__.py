# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Persons',
    'summary': """
        Manage duplicates, add several names and identifier""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'base',
        'contacts',
        'partner_usual_firstname',
        'mozaik_abstract_model',
        'mozaik_duplicate',
        'mozaik_partner_assembly',
    ],
    'data': [
        'data/ir_sequence.xml',
        'data/ir_cron.xml',
        'security/res_groups.xml',
        'security/res_partner.xml',
        'views/res_partner.xml',
        'views/person_menu.xml',
        'wizards/create_user_from_partner_view.xml',
        'wizards/allow_duplicate_view.xml',
    ],
    'demo': [
        'demo/res_partner.xml',
    ],
    'installable': True,
}
