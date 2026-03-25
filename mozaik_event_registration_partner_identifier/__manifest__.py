# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Registration Partner Identifier",
    "summary": """
        Allow to search event registrations by partner identifier.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        # Odoo
        "event",
        # OCA/server-tools
        "base_view_inheritance_extension",
        # Mozaik
        "mozaik_person",
    ],
    "data": ["views/event_registration.xml"],
    "demo": [],
}
