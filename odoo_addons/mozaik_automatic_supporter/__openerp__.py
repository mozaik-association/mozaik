# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Automatic Supporter',
    'description': """
        Transform automatically a contact into a supporter
        when creating involvements of such a category""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'mail',
        'mozaik_person',
        'mozaik_membership',
    ],
    'data': [
        'views/partner_involvement_category.xml',
    ],
    'demo': [
    ],
}
