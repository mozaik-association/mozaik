# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Survey Membership Request Involvement",
    "summary": """
        Creates a membership request from event registrations""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_membership_request_autovalidate",
        "mozaik_membership_request_from_registration",
        "mozaik_survey_involvement_category",
        "mozaik_survey_is_private",
        "mozaik_survey_question_involvement_category",
    ],
    "data": [
        "views/res_partner.xml",
        "views/membership_request.xml",
        "views/survey_survey.xml",
        "views/survey_question.xml",
    ],
}
