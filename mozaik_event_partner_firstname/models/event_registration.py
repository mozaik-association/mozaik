# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = ["event.registration"]

    firstname = fields.Char(
        string="First Name",
        compute="_compute_firstname",
        store=True,
        readonly=False,
    )
    lastname = fields.Char(
        string="Last Name",
        compute="_compute_lastname",
        store=True,
        readonly=False,
    )
    name = fields.Char(
        compute="_compute_name",
        inverse="_inverse_name_after_cleaning_whitespace",
        required=False,
        store=True,
        readonly=False,
    )

    @api.depends("partner_id.name")
    def _compute_firstname(self):
        for record in self:
            if record.partner_id:
                record.firstname = record.partner_id.firstname

    @api.depends("partner_id.name")
    def _compute_lastname(self):
        for record in self:
            if record.partner_id:
                record.lastname = record.partner_id.lastname

    @api.depends("firstname", "lastname")
    def _compute_name(self):
        """Write the 'name' field according to splitted data."""
        for record in self:
            record.name = self.env["res.partner"]._get_computed_name(
                record.lastname, record.firstname
            )

    def _inverse_name_after_cleaning_whitespace(self):
        for record in self:
            clean = self.env["res.partner"]._get_whitespace_cleaned_name(record.name)
            record.name = clean
            parts = self.env["res.partner"]._get_inverse_name(
                record.name, record.partner_id.is_company
            )
            record.lastname = parts["lastname"]
            record.firstname = parts["firstname"]

    def _get_website_registration_allowed_fields(self):
        res = super()._get_website_registration_allowed_fields()
        res.update(["firstname", "lastname"])
        return res
