# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Involvement",
    "summary": """
        Creates a membership request and adds involvements from event registrations""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_event_is_private",
        "mozaik_event_partner_firstname",
        "mozaik_event_question_thesaurus",
        "mozaik_event_thesaurus",
        "mozaik_involvement_thesaurus",
        "mozaik_membership_request",
    ],
    "data": [
        "views/event_event.xml",
        "views/partner_involvement.xml",
        "views/partner_involvement_category.xml",
    ],
    "demo": [],
}
