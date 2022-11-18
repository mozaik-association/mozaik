# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Survey Export Csv",
    "summary": """
        Implements a custom csv export for survey answers.""",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "contacts",
        "survey",
        "mozaik_ama_export",
        "mozaik_membership",
        "mozaik_person",
        "mozaik_thesaurus",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/survey_export.xml",
        "views/survey_survey.xml",
    ],
    "demo": [],
}
