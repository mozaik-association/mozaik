# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mozaik: All Modules Loader",
    "summary": """
        Loads all Mozaik modules""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "category": "Political Association",
    "depends": [
        # 'disable_tracking_installation',
        # 'disable_user_welcome_message',
        "inherit_abstract_view",
        # 'ir_rule_child_of',
        # 'mail_job_priority',
        "mozaik_abstract_model",
        # 'mozaik_account',
        "mozaik_address",
        "mozaik_address_local_street",
        # 'mozaik_communication',
        # 'mozaik_coordinate',
        "mozaik_duplicate",
        # 'mozaik_email',
        # 'mozaik_involvement',
        # 'mozaik_membership',
        "mozaik_partner_assembly",
        "mozaik_partner_fields",
        # 'mozaik_partner_unauthorized',
        "mozaik_person",
        # 'mozaik_phone',
        # 'mozaik_relation_coordinate',
        "mozaik_structure",
        # 'mozaik_subscription_price',
        "mozaik_thesaurus",
        # 'mozaik_tools',
        # 'mozaik_virtual_assembly_instance',
        # 'mozaik_virtual_partner_instance',
        # 'mozaik_virtual_partner_involvement',
        # 'mozaik_virtual_partner_membership',
        # 'mozaik_virtual_partner_relation',
        # 'partner_usual_firstname',
        "mozaik_mandate",
        "mozaik_mandate_female_label",
        "mozaik_mandate_category_sequence",
        # 'mozaik_membership_mandate',
        # 'mozaik_virtual_partner_mandate',
    ],
    "data": [
        # 'views/mail_followers.xml',
    ],
    "installable": True,
}
