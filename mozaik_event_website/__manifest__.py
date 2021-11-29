# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Website",
    "summary": """
        This addon add new field to manage website domains on events""",
    "version": "14.0.1.1.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": ["website_event"],
    "data": [
        "security/acl_event_website_domain.xml",
        "views/event_website_domain.xml",
        "views/event.xml",
    ],
}
