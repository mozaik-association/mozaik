# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Tickbox Question",
    "summary": """
        This module adds tickbox questions
        to website_event_questions""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_event_export",
        "mozaik_event_question_event_type",
        "mozaik_event_membership_request_involvement",
    ],
    "data": [
        "views/event_question.xml",
        "views/event_event.xml",
        "views/event_templates.xml",
        "views/event_registration.xml",
    ],
}
