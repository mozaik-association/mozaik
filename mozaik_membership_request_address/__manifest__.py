# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Request Address",
    "summary": """
        Implements a cron that deletes addresses not linked
        to a partner and not linked to a not validated membership request.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_address",
        "mozaik_membership_request",
    ],
    "data": [
        "data/ir_cron.xml",
    ],
    "demo": [],
}
