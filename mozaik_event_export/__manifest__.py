# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Export",
    "summary": """
        Implements a custom xls export for event registrations""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "event",
        "website_event_questions",
        "mozaik_ama_export",
        "mozaik_event_membership_request_involvement",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/event_export_xls.xml",
        "views/event_event.xml",
    ],
    "demo": [],
}
