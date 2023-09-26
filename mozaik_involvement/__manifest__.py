# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mozaik: Involvement",
    "summary": """
        Manage involvements (and all kind of segmentation) on partners""",
    "version": "14.0.1.1.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "category": "Political Association",
    "depends": [
        "base",
        "mail",
        "mozaik_abstract_model",
        "mozaik_owner_mixin",
        "mozaik_partner_assembly",
        "mozaik_thesaurus",
    ],
    "data": [
        "security/res_groups.xml",
        "security/partner_involvement_category.xml",
        "security/partner_involvement.xml",
        "views/partner_involvement.xml",
        "views/partner_involvement_category.xml",
        "views/involvement_menu.xml",
        "views/res_partner.xml",
    ],
    "demo": [
        "demo/partner_involvement_category.xml",
    ],
    "external_dependencies": {"python": ["openupgradelib"]},
    "installable": True,
}
