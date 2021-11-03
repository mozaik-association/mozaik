# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Website Event Track",
    "summary": """
        This module allows to see the event menu configuration
        even without activated debug mode""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        # Odoo
        "website_event_track",
    ],
    "data": [
        "views/event_event.xml",
    ],
}
