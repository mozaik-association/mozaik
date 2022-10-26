# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Request Sensitive Data",
    "summary": """
        If partner is recognized on the membership request, sensitive data
        (such as name, firstname, email, ...) are not always erasing data
        on the partner: if a value was already set on the partner, only
        an authenticated user can change these data
        (not a force autovalidate). Hence we prevent from changing these
        values, and we schedule an activity to an Odoo user.
        A system parameter defines which field has to be considered as 'sensitive'.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_membership_request_autovalidate",
        "mozaik_address",
    ],
    "data": [
        "data/ir_config_parameter.xml",
        "views/membership_request.xml",
    ],
    "demo": [],
}
