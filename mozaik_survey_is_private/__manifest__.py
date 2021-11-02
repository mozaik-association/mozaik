# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Survey Is Private",
    "summary": """
        This module create record rules
        depending on if the survey is private or not.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        # Mozaik
        "mozaik_single_instance",
        "mozaik_survey_thesaurus",
    ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/rules_survey_survey.xml",
        "views/survey_survey.xml",
    ],
}
