# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Petition Membership Request Origin",
    "summary": """Add origin 'Petition' to membership requests created from petitions.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_petition_membership_request_involvement",
        "mozaik_membership_request_origin",
    ],
    "data": ["data/membership_request_origin.xml"],
}
