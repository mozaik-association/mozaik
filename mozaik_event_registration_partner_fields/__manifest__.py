# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Registration Partner Fields",
    "summary": """
        Add zip field on event registrations. This field can be filled on website.,
        Allow to fill mobile when registering through the website.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "website_event",
    ],
    "data": [
        "views/event_registration.xml",
        "views/event_templates.xml",
    ],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
}
