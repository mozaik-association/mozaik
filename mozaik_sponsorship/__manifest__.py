# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Sponsorship",
    "summary": """
        Adds a sponsorship system (sponsors and godchildren) between partners.
        Specifying a sponsor on a membership request can offer a free membership
        to the godchild.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_membership",
        "mozaik_membership_request",
    ],
    "data": [
        "views/res_partner.xml",
        "views/membership_request.xml",
    ],
    "demo": [],
}
