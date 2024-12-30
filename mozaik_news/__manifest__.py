# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mozaik News",
    "summary": """
        News App: blog news, privacy on news""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "category": "Political Association",
    "depends": [
        # Mozaik
        "mozaik_privacy_domain_mixin",
    ],
    "data": [
        "security/groups.xml",
        "security/mozaik_news.xml",
        "views/mozaik_news.xml",
        "views/menus.xml",
    ],
    "installable": True,
}
