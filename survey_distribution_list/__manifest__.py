# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Survey Distribution List",
    "summary": """
        This module adds the possibility to send surveys to a distribution list.""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Mozaik Association",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        # ODOO
        "survey",
        # MOZAIK
        "distribution_list",
    ],
    "data": ["wizards/survey_invite.xml"],
}
