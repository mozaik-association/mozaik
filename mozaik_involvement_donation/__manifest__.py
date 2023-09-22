# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Involvement Donation",
    "summary": """
        Adds a new type of involvement: donation.
        A donation is an involvement with a positive amount.
        It's a promise until the payment is received.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_involvement",
    ],
    "data": [
        "views/partner_involvement.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
}
