# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Ama Indexed On Website",
    "summary": """
        Adds a boolean to know if the ama object must be indexed on website or not.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "event",
        "survey",
    ],
    "data": [
        "security/res_groups.xml",
        "views/survey_survey.xml",
        "views/event_event.xml",
    ],
    "demo": [],
}
