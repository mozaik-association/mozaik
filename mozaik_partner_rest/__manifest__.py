# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Partner Rest",
    "summary": """This addon extends partner REST API.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "base_rest",
        "base_rest_pydantic",
        "extendable",
        "mozaik_address",
        "mozaik_country_rest",
        "mozaik_involvement_rest",
        "mozaik_membership",
        "mozaik_membership_rest",
        "mozaik_partner_disabled",
        "mozaik_partner_fields",
        "mozaik_partner_global_opt_out",
        "mozaik_partner_unemployed",
        "partner_firstname",
    ],
    "data": [],
    "external_dependencies": {
        "python": [
            "extendable_pydantic",
            "pydantic",
        ]
    },
}
