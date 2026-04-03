# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Mass Mailing Partner",
    "summary": "Adds a 'Mass Mailings' smart button on the partner form to see "
    "all mailings received by that partner.",
    "version": "14.0.1.0.0",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/mozaik-association/mozaik",
    "license": "AGPL-3",
    "depends": [
        "mass_mailing",
        "contacts",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/mailing_trace_partner_views.xml",
    ],
    "installable": True,
}
