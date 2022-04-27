# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Multi Website",
    "summary": """
        This addon add new field to manage website domains""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": ["mozaik_petition", "website_event"],
    "data": [
        "security/acl_website_domain.xml",
        "views/event.xml",
        "views/petition.xml",
        "views/website_domain.xml",
    ],
}
