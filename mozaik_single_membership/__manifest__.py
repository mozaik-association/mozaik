# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Single Membership",
    "summary": """
        Restrict membership lines usage:
        only one active membership line per partner
        (and not per (partner,instance)).""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_membership",
        "mozaik_virtual_partner_membership",
    ],
    "data": [
        "views/membership_line.xml",
        "views/virtual_partner_membership.xml",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
}
