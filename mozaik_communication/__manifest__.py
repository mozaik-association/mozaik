# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mozaik: Communication",
    "summary": """
        Manage several mass communication methods""",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "category": "Political Association",
    "depends": [
        "mail",
        "mass_mailing",
        "distribution_list",
        "mass_mailing_distribution_list",
        # "mass_mail_queue_job",
        "partner_contact_birthdate",
        "partner_contact_gender",
        "mozaik_abstract_model",
        "mozaik_address",
        "mozaik_structure",
        "mozaik_involvement",
        "mozaik_person",
        "mozaik_membership",
        "mozaik_membership_request",
        "mozaik_owner_mixin",
        "mozaik_single_instance",
        "mozaik_thesaurus",
        # from https://github.com/OCA/social
        "email_template_configurator",
    ],
    "data": [
        "views/membership_request.xml",
        "security/communication_security.xml",
        "security/mail_mass_mailing_group.xml",
        "security/ir.model.access.csv",
        "wizards/distribution_list_mass_function.xml",
        "views/distribution_list_line_template.xml",
        "views/distribution_list_line.xml",
        "views/distribution_list.xml",
        "views/mailing_trace.xml",
        "views/mail_mass_mailing.xml",
        "views/mailing_trace_report.xml",
        "views/mail_template.xml",
        "views/res_partner.xml",
        "views/abstract_virtual_model.xml",
        "views/virtual_target.xml",
        "views/communication_menu.xml",
        "wizards/export_csv.xml",
    ],
    "demo": [
        "demo/res_partner.xml",
        "demo/distribution_list.xml",
    ],
    "installable": True,
    "external_dependencies": {"python": ["openupgradelib"]},
}
