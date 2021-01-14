# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class IntMandate(models.Model):
    _name = 'int.mandate'
    _description = "Internal Mandate"
    _inherit = ['abstract.mandate']

    _undo_redirect_action = 'mozaik_mandate.int_mandate_action'
    _unique_id_sequence = 0

    _unicity_keys = 'N/A'

    mandate_category_id = fields.Many2one(
        domain=[('type', '=', 'int')])
    int_assembly_id = fields.Many2one(
        comodel_name='int.assembly',
        string='Internal Assembly',
        index=True,
        required=True,
        domain=[('designation_int_assembly_id', '!=', False)])
    int_assembly_category_id = fields.Many2one(
        related='mandate_category_id.int_assembly_category_id',
        string='Internal Assembly Category',
        comodel_name="int.assembly.category")
    months_before_end_of_mandate = fields.Integer(
        string='Alert Delay (#Months)',
        track_visibility='onchange', group_operator='max')
    partner_instance_search_ids = fields.Many2many(
        relation="int_mandate_partner_instance_membership_rel",
    )
    instance_id = fields.Many2one(
        related="int_assembly_id.instance_id",
    )

    @api.constrains(
        'partner_id', 'int_assembly_id', 'mandate_category_id',
        'start_date', 'deadline_date')
    def _check_duplicate_mandates(self):
        self_sudo = self.sudo()
        allm = self_sudo.search([
            ('partner_id', 'in', self_sudo.mapped('partner_id').ids),
            ('int_assembly_id', 'in', self_sudo.mapped('int_assembly_id').ids),
            ('mandate_category_id', 'in',
             self_sudo.mapped('mandate_category_id').ids),
        ])
        for m in self_sudo:
            duplicates = allm.filtered(
                lambda s,
                p=m.partner_id, a=m.int_assembly_id, c=m.mandate_category_id,
                start=m.start_date, end=m.end_date or m.deadline_date:
                s.partner_id == p and
                s.int_assembly_id == a and
                s.mandate_category_id == c and
                s.start_date <= end and
                (s.end_date or s.deadline_date) >= start)
            if len(duplicates) > 1:
                raise ValidationError(_(
                    'A representative cannot have 2 identical mandates '
                    'during the same period!'
                ))

    @api.multi
    @api.onchange("mandate_category_id")
    def _onchange_mandate_category_id(self):
        for int_mandate in self:
            int_mandate.int_assembly_id = False
        return super()._onchange_mandate_category_id()

    @api.multi
    @api.onchange("int_assembly_id")
    def _onchange_int_assembly_id(self):
        for int_mandate in self:
            month = int_mandate.int_assembly_id.months_before_end_of_mandate
            assembly_id = int_mandate.int_assembly_id\
                .designation_int_assembly_id
            int_mandate.months_before_end_of_mandate = month
            int_mandate.designation_int_assembly_id = assembly_id
