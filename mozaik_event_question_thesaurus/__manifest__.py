# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Question Thesaurus",
    "summary": """
        This feature adds interests on answers of questions of type 'Selection'.
        """,
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_event_question_event_type",
        "mozaik_thesaurus",
    ],
    "data": [
        "views/event_event.xml",
        "views/event_question.xml",
    ],
}
