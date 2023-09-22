# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mass Mailing Distribution List",
    "summary": """
        Make the bridge between distribution list and mass mailing""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Mozaik Association",
    "website": "https://github.com/mozaik-association/mozaik",
    "category": "Marketing",
    "depends": ["distribution_list", "mass_mailing"],
    "data": [
        "data/ir_config_parameter.xml",
        "views/mailing_mailing.xml",
        "views/distribution_list.xml",
        "wizards/merge_distribution_list.xml",
    ],
    "installable": True,
}
