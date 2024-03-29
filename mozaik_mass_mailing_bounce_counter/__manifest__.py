# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Mass Mailing Bounce Counter",
    "summary": """
        Manages the email bounce counter on res.partner""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mass_mailing",
        "mozaik_communication",
    ],
    "data": [
        "security/res_groups.xml",
        "data/res_partner_data.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
}
