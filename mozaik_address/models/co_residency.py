# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CoResidency(models.Model):

    _name = "co.residency"
    _inherit = ["mozaik.abstract.model"]
    _description = "Co-Residency"
    _rec_name = "address_id"

    _unicity_keys = "address_id"

    address_id = fields.Many2one(
        comodel_name="address.address",
        string="Address",
        compute="_compute_address_id",
        store=True,
        readonly=True,
        index=True,
    )
    line = fields.Char("Line 1", tracking=True)
    line2 = fields.Char("Line 2", tracking=True)

    partner_ids = fields.One2many("res.partner", "co_residency_id", string="Partners")

    def name_get(self):
        """
        :rparam: list of (id, name)
                 where id is the id of each object
                 and name, the name to display.
        :rtype: [(id, name)] list of tuple
        """
        res = []
        for record in self:
            if not record.line and not record.line2:
                name = _("Co-Residency to complete")
            else:
                name = "/".join([line for line in [record.line, record.line2] if line])
            res.append((record["id"], name))
        return res

    @api.constrains("partner_ids")
    def _check_partner_ids(self):
        for co_residency in self:
            if any(not p.address_address_id for p in co_residency.partner_ids):
                raise ValidationError(_("All co-resident must have a address"))
            if len(co_residency.partner_ids.mapped("address_address_id")) == 0:
                raise ValidationError(_("There must be at least one co-resident"))
            if len(co_residency.partner_ids.mapped("address_address_id")) != 1:
                raise ValidationError(_("All co-resident must share the same address"))

    @api.depends("partner_ids", "partner_ids.address_address_id")
    def _compute_address_id(self):
        for co_residency in self:
            address_ids = co_residency.partner_ids.mapped("address_address_id")
            if len(address_ids) > 1:
                raise ValidationError(_("All co-resident must share the same address"))
            co_residency.address_id = address_ids

    def unlink(self):
        # trigger the duplicate detection when deleting the co-residency
        self.mapped("partner_ids").write({"co_residency_id": False})
        return super(CoResidency, self).unlink()
