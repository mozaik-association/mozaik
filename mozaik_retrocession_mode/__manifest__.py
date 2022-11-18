# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Retrocession Mode",
    "summary": """
        Add field retrocession_mode on mandates.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": [
        "mozaik_mandate",
    ],
    "data": [
        "views/sta_mandate.xml",
        "views/ext_mandate.xml",
    ],
}
