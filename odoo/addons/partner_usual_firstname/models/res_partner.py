# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    firstname = fields.Char(
        track_visibility='onchange',
    )
    lastname = fields.Char(
        track_visibility='onchange',
    )
    usual_firstname = fields.Char(
        track_visibility='onchange',
    )
    usual_lastname = fields.Char(
        track_visibility='onchange',
    )

    @api.multi
    @api.depends("firstname", "lastname", "usual_firstname", "usual_lastname")
    def _compute_name(self):
        """
        Rewrite without calling super() to use also usual_* fields.
        """
        for record in self:
            record.name = record._get_computed_name(
                record.usual_lastname or record.lastname,
                record.usual_firstname or record.firstname,
            )

    @api.multi
    def _inverse_name(self):
        """
        Rewrite without calling super() to replace also usual_* fields.
        """
        for record in self:
            parts = record._get_inverse_name(record.name, record.is_company)
            if record.usual_lastname and record.lastname:
                record.usual_lastname = parts['lastname']
            else:
                record.lastname = parts['lastname']
            if record.usual_firstname and record.firstname:
                record.usual_firstname = parts['firstname']
            else:
                record.firstname = parts['firstname']
            if record.lastname == record.usual_lastname:
                record.usual_lastname = False
            if record.firstname == record.usual_firstname:
                record.usual_firstname = False
