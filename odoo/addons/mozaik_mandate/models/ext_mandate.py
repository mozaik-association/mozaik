# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ExtMandate(models.Model):
    _name = 'ext.mandate'
    _description = "External Mandate"
    _inherit = ['abstract.mandate']
    _order = 'partner_id, ext_assembly_id, start_date, mandate_category_id'

    _undo_redirect_action = 'mozaik_mandate.ext_mandate_action'
    _unique_id_sequence = 400000000
    _unicity_keys = 'partner_id, ext_assembly_id, start_date, \
                         mandate_category_id'

    mandate_category_id = fields.Many2one(
        domain=[('type', '=', 'ext')])
    ext_assembly_id = fields.Many2one(
        comodel_name='ext.assembly',
        string='External Assembly',
        index=True,
        required=True)
    ext_assembly_category_id = fields.Many2one(
        related='mandate_category_id.ext_assembly_category_id',
        string='External Assembly Category',
        comodel_name="ext.assembly.category")
    competencies_m2m_ids = fields.Many2many(
        comodel_name='thesaurus.term',
        string='Remits')
    months_before_end_of_mandate = fields.Integer(
        string='Alert Delay (#Months)',
        track_visibility='onchange',
        group_operator='max')

    @api.multi
    @api.onchange("mandate_category_id")
    def _onchange_mandate_category_id(self):
        for ext_mandate in self:
            ext_mandate.ext_assembly_id = False
        return super()._onchange_mandate_category_id()

    @api.multi
    @api.onchange("ext_assembly_id")
    def _onchange_ext_assembly_id(self):
        for ext_mandate in self:
            ext_mandate.months_before_end_of_mandate = ext_mandate\
                .ext_assembly_id.months_before_end_of_mandate
            ext_mandate.designation_int_assembly_id = ext_mandate\
                .ext_assembly_id.designation_int_assembly_id
