# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Rest",
    "summary": """
        This module adds a controller for membershi REST services""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "base_rest",
        "base_rest_pydantic",
        "extendable",
        "mozaik_membership",
        "mozaik_membership_payment",
        "mozaik_membership_request_autovalidate",
        "mozaik_membership_request_from_registration",
        "mozaik_partner_global_opt_out",
        "mozaik_country_rest",
        "mozaik_distribution_list_rest",
        "mozaik_involvement_rest",
        "mozaik_partner_disabled",
        "mozaik_partner_unemployed",
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
