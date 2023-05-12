# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Virtual Partner Candidature",
    "summary": """
        Virtual model for candidatures.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "distribution_list",
        # "mozaik_partner_assembly",
        "mozaik_committee",
        "mozaik_communication",
        "mozaik_thesaurus",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/virtual_partner_candidature.xml",
    ],
    "demo": [],
}
