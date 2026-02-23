# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Request Autovalidate Light Rest",
    "summary": """Add autovalidation type to membership request rest services.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_membership_rest",
        "mozaik_membership_request_autovalidate_light",
    ],
    "data": [],
    "external_dependencies": {
        "python": [
            "extendable_pydantic<1",  # pylint:disable=missing-return
            "pydantic<2",  # pylint:disable=missing-return
        ]
    },
}
