# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Security Ama",
    "summary": """
        Manage security rules for events, petitions and surveys""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        # Odoo addons
        "survey",
        # Mozaik
        "mozaik_event_security",
        "mozaik_membership",
        "mozaik_petition",
        "mozaik_structure",
        "mozaik_survey_security",
    ],
    "data": [
        "views/survey_survey.xml",
        "views/event_event.xml",
        "views/petition_petition.xml",
        "security/rules_event.xml",
        "security/rules_petition.xml",
        "security/rules_survey.xml",
    ],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
}
