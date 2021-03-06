# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Involvement Follow-up',
    'description': """
        Manage follow-up of partner involvements""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'mail_restrict_follower_selection',
        'mail',
        'base_suspend_security',
        'mozaik_base',
        'mozaik_person',
        'mozaik_structure',
        'mozaik_mandate',
        'mozaik_membership',
    ],
    'data': [
        'security/partner_involvement.xml',
        'data/mail_message_subtype_data.xml',
        'data/ir_cron_data.xml',
        'data/ir_config_parameter.xml',
        'wizards/partner_involvement_followup_wizard.xml',
        'views/partner_involvement.xml',
        'views/partner_involvement_category.xml',
    ],
    'demo': [
    ],
}
