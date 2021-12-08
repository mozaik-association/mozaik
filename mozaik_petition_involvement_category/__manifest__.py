# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Petition Involvement Category",
    "summary": """
        Ability to associate to any petition an involvement category.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_involvement",
        "mozaik_petition",
    ],
    "data": [
        "views/petition_type.xml",
        "views/petition_petition.xml",
    ],
    "demo": [],
}
