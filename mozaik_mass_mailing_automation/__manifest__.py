# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Mass Mailing Automation",
    "summary": """
        Extension of mass mailing module to add an automation process:
        every day we check for new contacts in the mailing list and
        send them the mail.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mass_mailing",
        "mozaik_mass_mailing_access_rights",
    ],
    "data": [
        "views/mailing_mailing.xml",
    ],
    "demo": [],
}
