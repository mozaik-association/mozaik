# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Survey Thesaurus",
    "summary": """
        This feature adds field interest_ids
        (m2m to mozaik_thesaurus.thesaurus_term) to surveys
        """,
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_thesaurus",
        "survey",
    ],
    "data": [
        "views/survey_survey.xml",
    ],
    "demo": [],
}
