# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mozaik Document",
    "summary": """
        Documents App: content, folders, privacy on documents""",
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
        "security/mozaik_document.xml",
        "security/mozaik_document_folder.xml",
        "views/mozaik_document.xml",
        "views/mozaik_document_folder.xml",
        "views/menus.xml",
    ],
    "installable": True,
}
