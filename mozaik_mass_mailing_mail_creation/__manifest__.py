# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Mass Mailing Mail Creation",
    "summary": """
        This module rewrite Odoo code from mail and mass_mailing modules,
        in order to divide methods in sub-methods, to be able to extend them in
        inheriting sub-modules.
        This code DOESN'T has to be modified except if standard Odoo code is.
        """,
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mass_mailing",
    ],
    "data": [],
    "demo": [],
}
