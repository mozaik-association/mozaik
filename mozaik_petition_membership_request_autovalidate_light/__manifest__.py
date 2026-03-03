# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Petition Membership Request Autovalidate Light",
    "summary": """
        Allows to lightly auto-validate membership requests
        created from petition signatures""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_petition_membership_request_involvement",
        "mozaik_membership_request_autovalidate_light",
    ],
    "data": [
        "views/petition_petition.xml",
    ],
}
