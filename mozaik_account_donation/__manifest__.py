# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Account Donation",
    "summary": """
        Adds specific actions when reconciling a payment that must be a donation""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_account",
        "mozaik_involvement_donation",
    ],
    "data": [
        "data/product_product.xml",
        "views/membership_line.xml",
    ],
    "demo": [],
}
