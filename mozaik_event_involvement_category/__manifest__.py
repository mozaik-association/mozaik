# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Involvement Category",
    "summary": """
        Ability to associate to any event an involvement category.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "event",
        "mozaik_involvement",
    ],
    "data": [
        "views/event_event.xml",
        "views/event_type.xml",
    ],
    "demo": [],
}
