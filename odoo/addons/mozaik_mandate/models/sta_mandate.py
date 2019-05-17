# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StaMandate(models.Model):
    _name = 'sta.mandate'
    _description = "State Mandate"
    _inherit = ['abstract.mandate']
    _order = 'partner_id, sta_assembly_id, legislature_id, mandate_category_id'

    _allowed_inactive_link_models = ['sta.candidature']
    _undo_redirect_action = 'mozaik_mandate.sta_mandate_action'
    _unique_id_sequence = 200000000
    _unicity_keys = 'partner_id, sta_assembly_id, legislature_id,\
                         mandate_category_id'

    mandate_category_id = fields.Many2one(
        domain=[('type', '=', 'sta')])
    legislature_id = fields.Many2one(
        comodel_name='legislature',
        string='Legislature',
        index=True,
        required=True,
        track_visibility='onchange')
    sta_assembly_id = fields.Many2one(
        comodel_name='sta.assembly',
        string='State Assembly',
        index=True,
        required=True)
    sta_assembly_category_id = fields.Many2one(
        related='mandate_category_id.sta_assembly_category_id',
        string='State Assembly Category',
        type='many2one',
        comodel_name="sta.assembly.category",
        store=False,
        readonly=True)
    sta_power_level_id = fields.Many2one(
        related='sta_assembly_category_id.power_level_id',
        string='Power Level',
        comodel_name="sta.power.level",
        store=False,
        readonly=True)
    is_legislative = fields.Boolean(
        related='sta_assembly_id.is_legislative',
        store=True)
    competencies_m2m_ids = fields.Many2many(
        comodel_name='thesaurus.term',
        string='Remits')

    @api.constrains('legislature_id', 'start_date', 'deadline_date')
    def _check_legislature_date_consistency(self):
        self_sudo = self.sudo()
        for mandate in self_sudo:
            if not (mandate.legislature_id.start_date <=
                    mandate.start_date <= mandate.deadline_date <=
                    mandate.legislature_id.deadline_date):
                raise ValidationError(_(
                    'Mandate period is inconsistent with legislature period!'
                ))

    @api.multi
    @api.onchange("mandate_category_id")
    def _onchange_mandate_category_id(self):
        for mdt in self:
            if not mdt.mandate_category_id or \
                    mdt.mandate_category_id.sta_assembly_category_id != \
                    mdt.sta_assembly_id.assembly_category_id:
                mdt.sta_assembly_id = False
                continue
        return super()._onchange_mandate_category_id()

    @api.multi
    @api.onchange("legislature_id")
    def _onchange_legislature_id(self):
        for sta_mandate in self:
            sta_mandate.start_date = sta_mandate.legislature_id.start_date
            sta_mandate.deadline_date = sta_mandate.legislature_id\
                .deadline_date

    @api.multi
    @api.onchange("sta_assembly_id")
    def _onchange_sta_assembly_id(self):
        self.ensure_one()
        designation_int_assembly_id = False
        domain = [('is_designation_assembly', '=', True)]
        if self.sta_assembly_id:
            assembly = self.sta_assembly_id
            if assembly.assembly_category_id.is_legislative:
                designation_int_assemblies = assembly.electoral_district_ids\
                    .mapped("designation_int_assembly_id")
                domain = [('id', 'in', designation_int_assemblies.ids)]
            else:
                designation_int_assemblies = [
                    a
                    for a in assembly.instance_id.int_instance_id.assembly_ids
                    if a.is_designation_assembly
                ]
            if len(designation_int_assemblies) == 1:
                designation_int_assembly_id = \
                    designation_int_assemblies[0].id
        else:
            self.legislature_id = False
        self.designation_int_assembly_id = designation_int_assembly_id
        return {
            'domain': {
                'designation_int_assembly_id': str(domain),
            }
        }
