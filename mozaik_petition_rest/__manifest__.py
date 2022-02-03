# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Petition Rest",
    "summary": """
        Add a REST API to manage Petition""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "base_rest",
        "base_rest_pydantic",
        "extendable",
        "mozaik_petition",
        "mozaik_petition_thesaurus",
        "mozaik_thesaurus_api",
        "pydantic",
    ],
    "data": [],
    "external_dependencies": {
        "python": [
            "extendable_pydantic",
            "pydantic",
        ]
    },
}
