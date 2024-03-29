# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Survey Mandatory Questions",
    "summary": """
        Adding mandatory questions such as name, email, in surveys.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "survey",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/survey_survey.xml",
        "views/survey_question_by_default.xml",
    ],
    "demo": [],
}
