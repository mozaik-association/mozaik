# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Request Origin",
    "summary": """Add origin to membership requests.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": ["mozaik_abstract_model", "mozaik_membership_request"],
    "data": [
        "security/membership_request_origin.xml",
        "views/membership_request_origin.xml",
        "views/membership_request.xml",
    ],
}
