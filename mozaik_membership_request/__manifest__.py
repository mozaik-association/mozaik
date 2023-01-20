# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mozaik: Membership Request",
    "summary": """
        Manage membership and modification requests""",
    "version": "14.0.1.0.4",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "category": "Political Association",
    "depends": [
        "base",
        "mozaik_abstract_model",
        "mozaik_structure",
        "mozaik_membership",
        "mozaik_address_local_street",
        "mozaik_thesaurus",
        "mozaik_tools",
        "mozaik_account",
        "statechart",
        "mozaik_email_lowered",
        # 'mozaik_involvement',
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/res_groups.xml",
        "security/membership_security.xml",
        "data/ir_config_parameter.xml",
        "data/ir_cron_membership.xml",
        "data/ir_cron_supporter.xml",
        "views/membership_request.xml",
        "views/res_partner.xml",
    ],
    "demo": [
        "demo/membership_request.xml",
    ],
    "installable": True,
    "external_dependencies": {"python": ["openupgradelib"]},
}
