# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Security",
    "summary": """
        Adds security groups and features""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_partner_disabled",
        "mozaik_partner_unemployed",
    ],
    "data": [
        "security/groups.xml",
        "views/res_partner.xml",
        "views/membership_request.xml",
    ],
    "demo": [],
}
