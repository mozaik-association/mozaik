# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Mass Mailing Access Rights",
    "summary": """
        New group: Mass Mailing Manager. Managers can edit
         and unlink mass mailings.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mass_mailing",
    ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/mailing_mailing.xml",
        "views/mail_template.xml",
    ],
    "demo": [],
}
