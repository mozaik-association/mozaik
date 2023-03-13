# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mozaik: Additional Fields",
    "summary": """
        Add some fields on partner form""",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "category": "Political Association",
    "depends": [
        "base",
        "mail",
        "partner_contact_personal_information_page",
        "partner_contact_birthdate",
        "partner_contact_gender",
        "partner_contact_nationality",
    ],
    "data": ["views/res_partner.xml"],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
}
