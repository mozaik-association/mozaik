# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Partner Firstname",
    "summary": """
        This module adds fields firstname
        and lastname on attendees.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        # OCA/partner-contact
        "partner_firstname",
        # Odoo
        "website_event",
    ],
    "data": [
        "views/event_templates.xml",
        "views/event_registration.xml",
    ],
}
