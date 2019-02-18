# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mozaik: Relation coordinate',
    'description': """
        Specify coordinates on relations between partners""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'base',
        'partner_multi_relation',
        'mozaik_address',
        'mozaik_email',
        'mozaik_phone',
    ],
    'data': [
        'security/partner_relation_security.xml',
        'views/res_partner_relation_all.xml',
        'views/res_partner.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
