# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import date

from odoo import api, models, fields
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)

WORKER_PIVOT = 10


def get_year_selection():
    curr_year = date.today().year
    return [('%s' % str(curr_year+n), '%s' %
             str(curr_year+n)) for n in range(2)]


class GenerateReference(models.TransientModel):

    _name = "generate.reference"
    _description = 'Generate References'

    nb_selected = fields.Integer(string='Selected Partners')
    nb_member_concerned = fields.Integer(string='Members')
    nb_candidate_concerned = fields.Integer(string='Member Candidates')
    nb_former_concerned = fields.Integer(string='Former Members')
    partner_ids = fields.Many2many(
        comodel_name="res.partner", ondelete="cascade", required=True)
    reference_date = fields.Selection(get_year_selection(), string='Year')
    go = fields.Boolean()

    @api.model
    def _get_selected_values(self):
        partner_obj = self.env['res.partner']
        partner_ids = []
        member_ids = []
        candidate_ids = []
        former_ids = []

        if self.env.context.get('active_domain'):
            active_domain = self.env.context.get('active_domain')
            partner_ids = partner_obj.search(active_domain)
        elif self.env.context.get('active_ids'):
            partner_ids = self.env.context.get('active_ids')

        if partner_ids:
            # search member with reference
            member_ids = partner_obj.search(
                [('membership_state_id.code', '=', 'member'),
                 ('id', 'in', partner_ids)])
            candidate_ids = partner_obj.search(
                [('membership_state_id.code', '=', 'member_candidate'),
                 ('id', 'in', partner_ids)])
            former_ids = partner_obj.search(
                [('membership_state_id.code', '=', 'former_member'),
                 ('id', 'in', partner_ids)])
        return partner_ids, member_ids, candidate_ids, former_ids

    @api.model
    def default_get(self, fields_list):
        """
        To get default values for the object.
        """
        res = super().default_get(fields_list)

        current_fields = ['nb_selected',
                          'nb_member_concerned',
                          'nb_candidate_concerned',
                          'nb_former_concerned',
                          'partner_ids',
                          'go',
                          'reference_date']

        if any(el in fields_list for el in current_fields):
            partner_ids, member_ids, candidate_ids, former_ids = \
                self._get_selected_values()

            res['nb_selected'] = len(partner_ids)
            res['nb_member_concerned'] = len(member_ids)
            res['nb_candidate_concerned'] = len(candidate_ids)
            res['nb_former_concerned'] = len(former_ids)
            concerned_ids = member_ids+candidate_ids+former_ids
            res['partner_ids'] = [(6, 0, concerned_ids.ids)]
            res['go'] = bool(concerned_ids)
            month = date.today().month
            year = date.today().year
            res['reference_date'] = str(month == 12 and year+1 or year)

        return res

    @api.multi
    def generate_reference(self):
        """
        Generate reference for all partners
        If concerned partner number is > to the ir.parameter value then
        call connector to delay this work
        **Note**
        ir.parameter or `WORKER_PIVOT`
        """

        try:
            parameter_obj = self.env['ir.config_parameter']
            worker_pivot = int(parameter_obj.get_param(
                'worker_pivot', WORKER_PIVOT))
        except ValueError:  # worker_pivot wasn't a integer
            worker_pivot = WORKER_PIVOT
        for wiz in self:
            partner_ids = wiz.partner_ids
            if len(partner_ids) > worker_pivot:
                self.with_delay().generate_reference_action(
                    partner_ids, wiz.reference_date)
            else:
                self.generate_reference_action(partner_ids, wiz.reference_date)

    @api.model
    @job(default_channel="root.generate_reference")
    def generate_reference_action(self, partner_ids, ref_date):
        """
        Generate reference for each partner
        """
        for partner_id in partner_ids:
            ref = partner_id._generate_membership_reference(ref_date)
            vals = {
                'reference': ref,
                'del_mem_card_date': False,
            }
            partner_id.write(vals)
            _logger.info(
                'Reference %s generated for partner [%s]', ref, partner_id)

        return
