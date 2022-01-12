# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    _allowed_inactive_link_models = ["res.partner"]
    _inactive_cascade = True

    sta_mandate_ids = fields.One2many(
        comodel_name="sta.mandate",
        inverse_name="partner_id",
        string="State Mandates",
        domain=[("active", "=", True)],
        context={"force_recompute": True},
    )
    sta_mandate_inactive_ids = fields.One2many(
        comodel_name="sta.mandate",
        inverse_name="partner_id",
        string="State Mandates (Inactive)",
        domain=[("active", "=", False)],
    )
    int_mandate_ids = fields.One2many(
        comodel_name="int.mandate",
        inverse_name="partner_id",
        string="Internal Mandates",
        domain=[("active", "=", True)],
        context={"force_recompute": True},
    )
    int_mandate_inactive_ids = fields.One2many(
        comodel_name="int.mandate",
        inverse_name="partner_id",
        string="Internal Mandates (Inactive)",
        domain=[("active", "=", False)],
    )
    ext_mandate_ids = fields.One2many(
        comodel_name="ext.mandate",
        inverse_name="partner_id",
        string="External Mandates",
        domain=[("active", "=", True)],
        context={"force_recompute": True},
    )
    ext_mandate_inactive_ids = fields.One2many(
        comodel_name="ext.mandate",
        inverse_name="partner_id",
        string="External Mandates (Inactive)",
        domain=[("active", "=", False)],
    )
    ext_mandate_count = fields.Integer(
        string="External Mandates Nbr", compute="_compute_mandate_assembly_count"
    )
    ext_assembly_count = fields.Integer(
        string="External Assemblies", compute="_compute_mandate_assembly_count"
    )

    def get_mandate_action(self):
        """
        return an action for an ext.mandate contains into the domain a
        specific tuples to get concerned mandates
        """
        self.ensure_one()
        res_ids = self._get_assemblies()._get_mandates().ids
        domain = [("id", "in", res_ids)]

        # get model's action to update its domain
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mozaik_mandate.ext_mandate_action"
        )
        action["domain"] = domain
        return action

    def _get_assemblies(self):
        """
        return the assemblies  of the current partner
        """
        self.ensure_one()
        assembly_model = "ext.assembly"
        if self.is_assembly:
            field = "partner_id"
        else:
            field = "ref_partner_id"
        domain = [(field, "=", self.id)]

        assembly_obj = self.env[assembly_model]
        assemblies = assembly_obj.search(domain)

        return assemblies

    def _compute_mandate_assembly_count(self):
        """
        count the number of assemblies linked to the current partner
        count the number of mandates linked to the assemblies of the
        current partner
        """
        for partner in self:
            assemblies = partner._get_assemblies()
            partner.ext_assembly_count = len(assemblies)
            partner.ext_mandate_count = len(assemblies._get_mandates())

    def add_mandate_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Add a new mandate"),
            "res_model": self._context.get("mandate_model"),
            "context": {"default_partner_id": self.id},
            "view_mode": "form",
            "target": "new",
        }
