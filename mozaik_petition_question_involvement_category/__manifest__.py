# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Petition Question Involvement Category",
    "summary": """
        Adds an involvement category (not mandatory) on questions and answers.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_involvement",
        "mozaik_petition",
    ],
    "data": [
        "views/petition_question.xml",
        "views/petition_petition.xml",
    ],
    "demo": [],
}
