# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Mass Mailing Sending Control",
    "summary": """
        For big mass mailings, add a wizard confirmation to ensure that
         the user is aware of the high number of recipients. He must copy
         this number in a field to be allowed to send the mail.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mass_mailing",
    ],
    "data": [
        "security/acl_mozaik_mass_mailing_sending_control.xml",
        "views/res_config_settings.xml",
        "wizards/mozaik_mass_mailing_sending_control.xml",
        "views/mailing_mailing.xml",
    ],
}
