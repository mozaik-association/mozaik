# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Survey Question Involvement Category",
    "summary": """
        Adds an involvement category (not mandatory) on answers.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_involvement",
        "mozaik_survey_mandatory_questions",
    ],
    "data": [
        "views/survey_question_by_default.xml",
        "views/survey_question.xml",
        "views/survey_survey.xml",
    ],
    "demo": [],
}
