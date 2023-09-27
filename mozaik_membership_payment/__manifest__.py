# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Payment",
    "summary": """
        Allow to pay membership with the website""",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        # Mozaik
        "mozaik_membership",
        "mozaik_membership_request",
        "mozaik_membership_request_autovalidate",
        "mozaik_account",
        "mozaik_payment",
        # Odoo
        "account",
        "payment",
    ],
    "data": [
        "views/membership_request.xml",
        "wizards/payment_link_wizard.xml",
        "views/payment_templates.xml",
        "views/membership_line.xml",
        "views/assets.xml",
    ],
    "demo": [],
}
