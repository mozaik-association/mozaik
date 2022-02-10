# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Security",
    "summary": """
        This module adds the field visible_on_website to Event and adds
        a new user group: reader.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        # Odoo
        "event",
        "website_event_questions",
    ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/event_event.xml",
        "views/event_menus.xml",
    ],
}
