# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Sepa Direct Debit",
    "summary": """
        This module adds a cron to add direct debit lines
        from unpaid membership lines.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "account_banking_sepa_direct_debit",
        "mozaik_account",
        "mozaik_membership",
        "mozaik_partner_banking_mandate",
    ],
    "data": ["data/ir_cron.xml"],
}
