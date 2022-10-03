# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Card",
    "summary": """
        Adds fields on res.partner to encode info
        about partners' membership cards.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_membership",
    ],
    "data": [
        "security/res_groups.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
}
