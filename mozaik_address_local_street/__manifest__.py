# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mozaik: Address Local Street",
    "summary": """
        Add a model which can be loeded from a referencial""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "category": "Political Association",
    "depends": [
        "contacts",
        "mail",
        "mozaik_address",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/address_local_street.xml",
        "views/address_address_view.xml",
    ],
    "demo": [
        "demo/address_local_street.xml",
        "demo/address_address.xml",
    ],
    "installable": True,
}
