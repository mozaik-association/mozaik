# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Account Payment Analytic Account",
    "summary": """
        This module allows to force an analytic account
        to set on 'membership fees' move lines.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": ["account_payment_order", "account_payment", "analytic"],
    "data": ["views/res_config_settings.xml"],
}
