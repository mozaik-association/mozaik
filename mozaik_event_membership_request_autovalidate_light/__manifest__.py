# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Membership Request Autovalidate Light",
    "summary": """
        Allows to lightly auto-validate membership requests
        created from event registrations""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_event_membership_request_involvement",
        "mozaik_membership_request_autovalidate_light",
    ],
    "data": [
        "views/event_event.xml",
    ],
}
