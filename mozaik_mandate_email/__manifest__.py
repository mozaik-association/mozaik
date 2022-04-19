# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Mandate Email",
    "summary": """
        Adds a second email field (mandate email) on partner form view.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_mandate",
    ],
    "data": [
        "security/groups.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
}
