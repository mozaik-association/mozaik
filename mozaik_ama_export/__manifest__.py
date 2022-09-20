# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Ama Export",
    "summary": """
        "Abstract" module giving tools for exporting data from ama objects
        (event, petition, survey)""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_membership",
        "mozaik_person",
        "partner_contact_gender",
    ],
    "data": [
        "security/ir.model.access.csv",
    ],
    "demo": [],
}
