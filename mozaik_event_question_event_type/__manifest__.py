# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Question Event Type",
    "summary": """
        This feature extends _compute_question_ids so that it is easier to
        add new fields on event.question.
        Moreover it adds a check preventing from changing the event type
        if there are already registered attendees.
        """,
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "website_event_questions",
    ],
    "data": [
        "views/event_event.xml",
    ],
}
