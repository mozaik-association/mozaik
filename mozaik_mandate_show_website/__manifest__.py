# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Mandate Show Website",
    "summary": """
        Adds booleans to decide if mandates will be visible on website or not.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_mandate",
    ],
    "data": [
        "views/ext_mandate.xml",
        "views/int_mandate.xml",
        "views/sta_mandate.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
}
