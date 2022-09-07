# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Interest Group",
    "summary": """
        Adds interests groups on involvement categories,
        to flag partners being into specific interest groups
        and allow some users to view only these partners.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_communication",
        "mozaik_involvement",
        "mozaik_person",
        "partner_multi_relation",
    ],
    "data": [
        "views/res_partner.xml",
        "security/ir.model.access.csv",
        "views/interest_group.xml",
        "views/partner_involvement_category.xml",
    ],
    "demo": [],
}
