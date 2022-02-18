# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Membership Request Involvement",
    "summary": """
        Creates a membership request from event registrations""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "event",
        "mozaik_event_involvement_category",
        "mozaik_event_question_involvement_category",
        "mozaik_event_partner_firstname",
        "mozaik_membership_request_autovalidate",
        "mozaik_membership_request_from_registration",
    ],
    "data": [
        "views/res_partner.xml",
        "views/event_event.xml",
        "views/event_registration.xml",
        "views/membership_request.xml",
    ],
    "demo": [],
}
