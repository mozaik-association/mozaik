# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Survey Scoring",
    "summary": """
        1. A question with scoring can be excluded from the score
        if the partner doesn't answer.
        2. The certification mail can be sent
        to partners even if they fail the certification.
        """,
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "survey",
    ],
    "data": [
        "views/survey_survey.xml",
    ],
    "demo": [],
}
