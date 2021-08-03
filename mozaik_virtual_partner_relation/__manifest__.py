# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Virtual partner relation',
    'version': '14.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    'category': 'Political Association',
    'depends': [
        'partner_contact_birthdate',
        'partner_contact_gender',
        'partner_multi_relation',
        'distribution_list',
        'mozaik_partner_assembly',
        'mozaik_relation_coordinate',
        'mozaik_communication',
        'mozaik_thesaurus',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/virtual_partner_relation.xml',
    ],
    'license': 'AGPL-3',
    "installable": False,
}
