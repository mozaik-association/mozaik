# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Virtual Model Single Instance",
    "summary": """
        Add partner_int_instance_id field on virtual models, in case of a
        single instance constraint on res.partner.
        Add specific fields / view options related to the single instance property
        to some particular virtual models.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_communication",
        "mozaik_single_instance",
        "mozaik_virtual_assembly_instance",
        "mozaik_virtual_partner_candidature",
        "mozaik_virtual_partner_mandate",
        "mozaik_virtual_partner_mass_mailing",
        "mozaik_virtual_partner_membership",
    ],
    "data": [
        "views/abstract_virtual_model.xml",
        "views/virtual_partner_mass_mailing.xml",
        "views/virtual_partner_membership.xml",
        "views/virtual_assembly_instance.xml",
    ],
    "demo": [],
}
