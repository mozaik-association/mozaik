# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Request From Registration",
    "summary": """
        Creating a membership request from a registration to
        an event / a petition / a survey.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "event",
        "mozaik_membership_request",
    ],
    "data": [
        "views/event_registration.xml",
    ],
    "demo": [],
}
