# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Involvement Donation Payment",
    "summary": """
        Manage payment acquirers for involvement donations""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        # Odoo
        "payment",
        # Mozaik
        "mozaik_involvement_donation",
        "mozaik_payment",
    ],
    "data": [
        "views/assets.xml",
        "views/partner_involvement.xml",
        "views/partner_involvement_category.xml",
        "views/payment_templates.xml",
    ],
    "demo": [],
}
