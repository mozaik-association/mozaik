# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Rest",
    "summary": """
        This module adds a controller for event REST services""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "event_rest_api",
        "mozaik_address",
        "mozaik_event_is_private",
        "mozaik_event_publish_date",
        "mozaik_event_stage_draft",
        "mozaik_event_thesaurus",
        "mozaik_event_website",
        "mozaik_thesaurus_api",
        "website_event",
    ],
    "data": [],
    "external_dependencies": {
        "python": [
            "pydantic",
        ]
    },
}
