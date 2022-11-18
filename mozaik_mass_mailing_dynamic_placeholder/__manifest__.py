# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Mass Mailing Dynamic Placeholder",
    "summary": """
        Adds dynamic placeholder templates on mass mailings.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "email_template_configurator",
        "mass_mailing",
        "mozaik_mass_mailing_access_rights",
    ],
    "data": [
        "views/mailing_mailing.xml",
        "views/email_template_placeholder.xml",
    ],
    "demo": [],
}
