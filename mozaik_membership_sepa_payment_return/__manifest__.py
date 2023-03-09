# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Sepa Payment Return",
    "summary": """
        This module processes payment returns for refused SEPA
        direct debit orders. It allows to match the payment return line
        with a partner, to delete the banking mandate and mark the
        membership line as unpaid.""",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        # Odoo
        "account",
        "mail",
        # OCA
        "account_banking_mandate",
        "account_banking_sepa_direct_debit",
        # Mozaik
        "mozaik_abstract_model",
        "mozaik_account",
        "mozaik_membership",
        "mozaik_membership_mark_as_unpaid",
    ],
    "data": [
        "security/groups.xml",
        "security/payment_return.xml",
        "security/process_payment_return.xml",
        "views/payment_return.xml",
        "data/mail_template.xml",
        "wizards/process_payment_return.xml",
    ],
    "demo": [],
}
