# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Partner Disabled",
    "summary": """
        Adds the boolean field 'disabled' on partners""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_membership_request",
    ],
    "data": [
        "views/membership_request.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
}
