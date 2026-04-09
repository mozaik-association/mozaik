# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Employee REST",
    "summary": """
        Expose employee""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        # Mozaik
        "mozaik_hr_work_address",
        # OCA/rest-framework
        "base_rest",
        "base_rest_pydantic",
        "extendable",
        "pydantic",
        # Odoo
        "hr",
    ],
    "data": [],
    "external_dependencies": {
        "python": [
            "extendable_pydantic<1",  # pylint:disable=missing-return
            "pydantic<2",  # pylint:disable=missing-return
        ]
    },
}
