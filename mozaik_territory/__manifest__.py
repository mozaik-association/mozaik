# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Territory",
    "summary": """Manage territories on contacts""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "contacts",
        "mozaik_thesaurus",
    ],
    "data": [
        "views/res_partner.xml",
        "security/territory.xml",
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/territory.xml",
    ],
}
