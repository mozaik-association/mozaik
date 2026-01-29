# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mozaik: Virtual partner employee",
    "summary": "Virtual model combining partner and employee information",
    "version": "14.0.1.0.0",
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "category": "Political Association",
    "depends": [
        "distribution_list",
        "hr",
        "mozaik_communication",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/virtual_partner_employee.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
