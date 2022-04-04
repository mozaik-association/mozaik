# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Mass Mailing Mail Server",
    "summary": """
        You can give to all mail servers a min and a max number of recipients.
        On a mass mailing, if you don't provide a mail server, Odoo will chose
        the one that fits with the number of recipients.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mass_mailing",
    ],
    "data": [
        "views/ir_mail_server.xml",
    ],
    "demo": [],
}
