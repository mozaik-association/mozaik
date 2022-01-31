# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Rest",
    "summary": """
        This module adds a controller for membershi REST services""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "base_rest",
        "base_rest_pydantic",
        "mozaik_membership",
    ],
    "data": [],
    "external_dependencies": {
        "python": [
            "pydantic",
        ]
    },
}
