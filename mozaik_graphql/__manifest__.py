# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Graphql",
    "summary": """
        GraphQL endpoint for Mozaik""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        # OCA
        "graphql_base",
        # Mozaik
        "mozaik_account",
        "mozaik_address",
        "mozaik_mandate",
        "mozaik_mandate_category_sequence",
        "mozaik_mandate_female_label",
        "mozaik_mandate_partner_fields",
        "mozaik_mandate_show_website",
        "mozaik_membership",
        "mozaik_membership_card",
        "mozaik_membership_mandate",
        "mozaik_partner_fields",
        "mozaik_person_deceased",
        "mozaik_structure",
        "mozaik_thesaurus",
        "mozaik_web_image_route",
    ],
    "external_dependencies": {"python": ["graphene"]},
}
