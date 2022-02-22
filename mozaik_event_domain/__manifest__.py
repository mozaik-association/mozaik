# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Domain",
    "summary": """
        Adds a domain on an event to limit the access""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "event",
        "mozaik_security_ama",
    ],
    "data": [
        "views/event_event.xml",
    ],
    "demo": [],
}
