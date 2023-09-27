# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Virtual Partner Involvement Donation",
    "summary": """
        Improves the virtual Partner/Involvement model
        by adding donations related fields.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_involvement_donation",
        "mozaik_virtual_partner_involvement",
    ],
    "data": [
        "views/virtual_partner_involvement.xml",
    ],
}
