# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Question Involvement Category",
    "summary": """
        Adds an involvement category (not mandatory) on questions and answers.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_event_question_event_type",
        "mozaik_involvement",
    ],
    "data": [
        "views/event_question.xml",
        "views/event_event.xml",
    ],
    "demo": [],
}
