# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Last Changes Report",
    "summary": """
        Log several change types on membership lines.
        Define a cron to periodically send by email a summary of all changes occurred
        for a given instance. This cron is archived by default, as the mail template
        subject and body must be filled.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_address",
        "mozaik_involvement",
        "mozaik_mandate",
        "mozaik_membership",
        "mozaik_partner_global_opt_out",
        "mozaik_structure",
    ],
    "data": [
        "views/membership_line.xml",
        "views/mandate_category.xml",
        "views/partner_involvement.xml",
        "views/partner_involvement_category.xml",
        "data/mail_template.xml",
        "data/ir_cron.xml",
    ],
    "demo": [],
}
