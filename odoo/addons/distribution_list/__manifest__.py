# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Distribution List',
    'version': '11.0.1.0.0',
    'author': 'ACSONE SA/NV',
    'maintainer': 'ACSONE SA/NV',
    "website": "http://www.acsone.eu",
    'category': 'Marketing',
    'depends': [
        'base',
        'web',
        'mail',
    ],
    'description': """
Distribution List
=================
This module provide features to allow the user to
* create distribution lists composed with dynamic filters (odoo domain)
* manage those distribution lists by adding or deleting lines
""",
    'data': [
        'security/distribution_list_security.xml',
        'security/ir.model.access.csv',
        'views/distribution_list.xml',
        'views/distribution_list_line.xml',
        'wizard/distribution_list_add_filter.xml',
        'wizard/mail_compose_message.xml',
        'wizard/merge_distribution_list.xml',
        'data/mail_template.xml',
    ],
    'demo': [
        'demo/company_data.xml',
        'demo/res_partner.xml',
        'demo/res_users.xml',
        'demo/distribution_list.xml',
        'demo/distribution_list_line.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
