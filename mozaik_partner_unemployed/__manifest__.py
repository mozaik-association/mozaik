# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Partner Unemployed",
    "summary": """
        Add the boolean 'unemployed' feature.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_membership_request",
    ],
    "data": [
        "views/membership_request.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
}