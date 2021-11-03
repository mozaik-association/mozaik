# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Is Private",
    "summary": """
        This module adds the field visible_on_website to Event and create
        record rules depending on if the event is private or not.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        # Mozaik
        "mozaik_single_instance",
        # Odoo
        "event",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/rules_event_event.xml",
        "views/event_event.xml",
    ],
}
