# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Sponsorship Rest",
    "summary": """
        Adds REST logic for module mozaik_sponsorship""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_sponsorship",
        "mozaik_membership_rest",
        "mozaik_partner_rest",
    ],
    "data": [],
    "demo": [],
    "external_dependencies": {
        "python": [
            "pydantic",
        ]
    },
}
