# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Thesaurus Rest",
    "summary": """
        Add a REST API to manage distribution list""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "base_rest",
        "base_rest_pydantic",
        "distribution_list",
        "extendable",
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
