# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Distribution List",
    "summary": """
        Manage distribution lists composed
        with multiple filters (odoo domain)""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "category": "Marketing",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/distribution_list_security.xml",
        "security/ir.model.access.csv",
        "views/distribution_list.xml",
        "views/distribution_list_line_template.xml",
        "views/distribution_list_line.xml",
        "wizards/distribution_list_add_filter.xml",
        "wizards/mail_compose_message.xml",
        "wizards/merge_distribution_list.xml",
        "data/mail_template.xml",
    ],
    "demo": [
        "demo/res_company.xml",
        "demo/res_partner.xml",
        "demo/res_users.xml",
        "demo/distribution_list.xml",
        "demo/distribution_list_line.xml",
    ],
    "sequence": 1000,
    "installable": True,
}
