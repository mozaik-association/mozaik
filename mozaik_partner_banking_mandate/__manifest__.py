# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Partner Banking Mandate",
    "summary": """
        This module adds a flag on partners with valid mandate(s).""",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "depends": ["account_banking_mandate", "mozaik_virtual_partner_membership"],
    "data": ["views/virtual_partner_membership.xml", "views/res_partner.xml"],
}
