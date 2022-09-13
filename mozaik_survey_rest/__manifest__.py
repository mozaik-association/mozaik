# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Survey Rest",
    "summary": """
        This module adds REST services for surveys""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "base_rest",
        "base_rest_pydantic",
        "survey",
        "mozaik_ama_indexed_on_website",
        "mozaik_survey_publish_date",
        "mozaik_survey_membership_request_involvement",
        "mozaik_thesaurus_api",
        "mozaik_web_image_route",
        "extendable",
        "pydantic",
    ],
    "data": [],
    "demo": [],
    "external_dependencies": {
        "python": [
            "extendable_pydantic",
            "pydantic",
        ]
    },
}
