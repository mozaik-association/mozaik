# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mozaik: Persons",
    "summary": """
        Manage duplicates, add several names and identifier""",
    "version": "14.0.1.0.3",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "category": "Political Association",
    "depends": [
        "base",
        "mail",
        "contacts",
        "base_user_role",
        "partner_firstname",
        "partner_usual_firstname",
        "partner_contact_birthdate",
        "mozaik_tools",
        "mozaik_abstract_model",
        "mozaik_duplicate",
        "mozaik_partner_assembly",
        "mozaik_address",
        "mozaik_address_local_street",
    ],
    "data": [
        "data/ir_sequence.xml",
        "data/ir_cron.xml",
        "security/res_groups.xml",
        "security/res_partner.xml",
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/person_menu.xml",
        "wizards/create_user_from_partner_view.xml",
        "wizards/allow_duplicate_view.xml",
    ],
    "demo": [
        "demo/res_partner.xml",
    ],
    "installable": True,
}
