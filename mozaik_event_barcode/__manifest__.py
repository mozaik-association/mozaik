# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Barcode",
    "summary": """
        Adds barcodes on event.registration records.
        Adds a button from event.event form view to access a page from where
        the event organizer can scan barcodes to confirm the attendance of the partners.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "event",
        "mozaik_event_membership_request_involvement",
        "mozaik_event_partner_firstname",
        "mozaik_virtual_partner_membership",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/barcode_scanner.xml",
        "views/event_event.xml",
        "views/event_report_templates.xml",
        "views/event_registration.xml",
    ],
    "demo": [],
}
