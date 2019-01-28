# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IntMandate(models.Model):
    _name = 'int.mandate'
    _description = "Internal Mandate"
    _inherit = ['abstract.mandate']
    _order = 'partner_id, int_assembly_id, start_date, mandate_category_id'

    _allowed_inactive_link_models = ['int.candidature']
    _undo_redirect_action = 'mozaik_mandate.int_mandate_action'
    _unique_id_sequence = 0

    _unicity_keys = 'partner_id, int_assembly_id, start_date,\
                        mandate_category_id'

    unique_id = fields.Integer(
        compute="_compute_unique_id",
        store=True)
    mandate_category_id = fields.Many2one(
        comodel_name='mandate.category',
        string='Mandate Category',
        index=True,
        required=True,
        track_visibility='onchange',
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
    is_submission_mandate = fields.Boolean(
        related='mandate_category_id.is_submission_mandate',
        string='With Wages Declaration',
        help='Submission to a Mandates and Wages Declaration',
        store=True)
    is_submission_assets = fields.Boolean(
        related='mandate_category_id.is_submission_assets',
        string='With Assets Declaration',
        help='Submission to a Mandates and Assets Declaration',
        store=True)
    months_before_end_of_mandate = fields.Integer(
        string='Alert Delay (#Months)',
        track_visibility='onchange', group_operator='max')

    @api.multi
    @api.onchange("mandate_category_id")
    def onchange_mandate_category_id(self):
        for int_mandate in self:
            int_mandate.int_assembly_id = False

    @api.multi
    @api.onchange("int_assembly_id")
    def onchange_int_assembly_id(self):
        for int_mandate in self:
            month = int_mandate.int_assembly_id.months_before_end_of_mandate
            assembly_id = int_mandate.int_assembly_id\
                .designation_int_assembly_id
            int_mandate.months_before_end_of_mandate = month
            int_mandate.designation_int_assembly_id = assembly_id
