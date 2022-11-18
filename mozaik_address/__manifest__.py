# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "MOZAIK: Address",
    "summary": """
        Module for addresses, postal coordinates and co-residencies""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "category": "Political Association",
    "depends": [
        "base",
        "mail",
        "contacts",
        "base_address_city",
        "mozaik_tools",
        "mozaik_abstract_model",
    ],
    "data": [
        "wizards/change_address.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/address_address.xml",
        "data/res_country.xml",
        "views/co_residency.xml",
        "views/res_city.xml",
        "views/res_partner.xml",
        "wizards/create_co_residency_address.xml",
    ],
    "demo": [
        "demo/res_city.xml",
        "demo/res_partner.xml",
        "demo/address_address.xml",
    ],
    "installable": True,
}
