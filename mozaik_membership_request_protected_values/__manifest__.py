# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Request Protected Values",
    "summary": """
        Allows to protect values to avoid changes in onchange_partner_id_vals
        when changing the partner or request type on a membership request.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_membership_request",
    ],
    "data": [
        "security/groups.xml",
        "views/membership_request.xml",
    ],
    "demo": [],
}
