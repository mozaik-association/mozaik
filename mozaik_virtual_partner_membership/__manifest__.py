# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mozaik: Virtual partner membership",
    "version": "14.0.1.0.0",
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "category": "Political Association",
    "depends": [
        "distribution_list",
        "mozaik_account",
        "mozaik_communication",
        "mozaik_membership",
        "mozaik_thesaurus",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/virtual_partner_membership.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
