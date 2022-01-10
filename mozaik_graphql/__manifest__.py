# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Graphql",
    "summary": """
        GraphQL endpoint for Mozaik""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        # OCA
        "graphql_base",
        # Mozaik
        "mozaik_mandate",
        "mozaik_mandate_category_sequence",
        "mozaik_mandate_female_label",
        "mozaik_membership",
        "mozaik_membership_mandate",
        "mozaik_structure",
        "mozaik_thesaurus",
    ],
    "external_dependencies": {"python": ["graphene"]},
}