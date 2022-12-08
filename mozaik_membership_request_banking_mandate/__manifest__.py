# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Request Banking Mandate",
    "summary": """
        This module adds the possibility to add bank accounts
        and mandates from membership requests.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": ["account_banking_mandate", "mozaik_membership_request_autovalidate"],
    "data": ["views/membership_request.xml"],
}
