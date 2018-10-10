# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.fields import first
from odoo.tools.safe_eval import safe_eval


class IntInstance(models.Model):

    _inherit = 'int.instance'
    member_count = fields.Integer(
        compute='_compute_member_count', string='Members')
    partner_ids = fields.One2many(
        comodel_name="res.partner", inverse_name="int_instance_id")
    partner_m2m_ids = fields.Many2many(
        comodel_name="res.partner")

    @api.multi
    @api.depends("partner_ids")
    def _compute_member_count(self):
        for inst in self:
            inst.member_count = len(inst.partner_ids.filtered(
                lambda p, ii=inst:
                p.int_instance_id == ii and not p.is_company))

    @api.multi
    def get_member_action(self):
        self.ensure_one()
        action = self.env.ref(
            "mozaik_person.res_partner_natural_person_action").read()[0]
        domain = safe_eval(action['domain'])
        action['domain'] = domain + [('int_instance_id', '=', self.id)]
        return action

    @api.model
    def create(self, vals):
        if not vals.get('parent_id'):
            if not self.env.user._is_admin():
                # because the user has rights to create a new instance
                # this new instance has to be added to users's internal
                # instances if it is a root instance
                u = self.env.user
                vals["partner_m2m_ids"] = [(4, u.partner_id.id)]
        res = super().create(vals)
        self.env['ir.rule'].clear_caches()
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'parent_id' in vals:
            self.env['ir.rule'].clear_caches()
        return res

    @api.multi
    def unlink(self):
        res = super().unlink()
        self.env['ir.rule'].clear_caches()
        return res

    @api.model
    def _get_default_int_instance(self):
        """
        Returns the default Internal Instance
        """
        res = super()._get_default_int_instance()
        if not res:
            res = first(self.env['res.users']._internal_instances())
        return res
