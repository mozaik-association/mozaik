# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik: Account",
    "summary": """
        Manage membership reconciliation""",
    "version": "14.0.2.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "category": "Political Association",
    "depends": [
        "product",
        "account",
        "mozaik_membership",
        "l10n_generic_coa",
        # OCA/account-reconcile
        "account_reconciliation_widget",
        # OCA/bank-statement-import
        "account_statement_import",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "wizards/update_membership.xml",
        "views/account_bank_statement.xml",
        "views/product_template.xml",
        "views/res_partner.xml",
        "views/membership_line.xml",
        "views/account_move_line.xml",
    ],
    "demo": ["demo/product_product.xml", "demo/ir_property.xml"],
    "installable": True,
}
