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
        "event_sale",
        "mozaik_address",
        "mozaik_ama_indexed_on_website",
        "mozaik_event_image",
        "mozaik_event_description",
        "mozaik_event_publish_date",
        "mozaik_event_registration_partner_fields",
        "mozaik_event_security",
        "mozaik_event_stage_draft",
        "mozaik_event_thesaurus",
        "mozaik_event_tickbox_question",
        "mozaik_thesaurus_api",
        "website_event",
        "website_event_questions",
        "mozaik_web_image_route",
        "mozaik_website_multi",
        "pydantic",
    ],
    "data": ["views/event_event.xml"],
    "external_dependencies": {
        "python": [
            "extendable_pydantic",
            "pydantic",
        ]
    },
}
