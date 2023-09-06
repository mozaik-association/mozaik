# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Barcode Question",
    "summary": """
        The answers to some questions on event.registrations will appear in the
        barcode scanner wizard (after the registration is retrieved).
        Configure on each event.question if this question must appear
        in the wizard or not.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        # Odoo
        "website_event_questions",
        # Mozaik
        "mozaik_event_barcode",
        "mozaik_event_tickbox_question",
    ],
    "data": [
        "wizards/barcode_scanner.xml",
        "views/event_event.xml",
        "views/event_question.xml",
    ],
}
