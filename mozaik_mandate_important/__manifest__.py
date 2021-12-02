# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Mandate Important",
    "summary": """
        This addon allows to mark some mandates as 'important'""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_mandate",
        "mozaik_virtual_assembly_instance",
        "mozaik_virtual_partner_mandate",
    ],
    "data": [
        "views/ext_assembly.xml",
        "views/ext_mandate.xml",
        "views/virtual_assembly_instance.xml",
        "views/virtual_partner_mandate.xml",
    ],
}
