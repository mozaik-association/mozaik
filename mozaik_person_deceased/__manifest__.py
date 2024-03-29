# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Person Deceased",
    "summary": """
        Clean and archive res.partner records when people are deceased""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_partner_fields",
        "mozaik_person",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/deceased_partner.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
}
