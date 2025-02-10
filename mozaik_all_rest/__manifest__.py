# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mozaik: All REST Modules Loader",
    "summary": """
        Loads all REST Mozaik modules""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "category": "Political Association",
    "depends": [
        "mozaik_country_rest",
        "mozaik_distribution_list_rest",
        "mozaik_event_rest",
        "mozaik_event_stage_draft",
        "mozaik_involvement_rest",
        "mozaik_involvement_donation_rest",
        "mozaik_mail_rest",
        "mozaik_membership_rest",
        "mozaik_partner_rest",
        "mozaik_petition_rest",
        "mozaik_survey_rest",
        "mozaik_thesaurus_api",
    ],
    "installable": True,
}
