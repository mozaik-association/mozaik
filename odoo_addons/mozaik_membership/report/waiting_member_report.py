# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import tools
from openerp import api, fields, models

DEFAULT_NB_DAYS = 30

_logger = logging.getLogger(__name__)


class waiting_member_report(models.Model):

    _name = "waiting.member.report"
    _description = 'Members Committee'
    _auto = False

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Member')
    membership_state_id = fields.Many2one(
        comodel_name='membership.state', string='Status')
    int_instance_id = fields.Many2one(
        comodel_name='int.instance', string='Internal Instance')
    identifier = fields.Integer(group_operator='min')
    nb_days = fields.Integer(string='#Days', group_operator='max')

    _order = "nb_days desc, partner_id"

    def init(self, cr):
        """
        View that takes all partners where the status is into a
        one-month waiting acceptance since one month or more
        """
        tools.drop_view_if_exists(cr, 'waiting_member_report')
        cr.execute("""
            create or replace view waiting_member_report as (
                SELECT
                    p.id as id,
                    p.id as partner_id,
                    p.identifier as identifier,
                    ms.id as membership_state_id,
                    ml.int_instance_id as int_instance_id,
                    ABS(EXTRACT
                        (year FROM age(ml.date_from))*365 +
                    EXTRACT
                        (month FROM age(ml.date_from))*30 +
                    EXTRACT
                        (day FROM age(ml.date_from))) AS
                    nb_days
                FROM res_partner p
                JOIN membership_state ms
                    ON ms.id = p.membership_state_id
                JOIN
                    membership_line ml
                    ON ml.partner_id = p.id
                WHERE
                    p.is_company = false AND
                    ml.active = true AND
                    ms.code IN
                    ('member_committee', 'former_member_committee')
            )
        """)

    @api.model
    def _process_accept_members(self):
        """
        Advance the workflow with the signal `accept`
        for all partners found
        """
        nb_days = self.env['ir.config_parameter'].get_param(
            'nb_days', default=DEFAULT_NB_DAYS)

        try:
            nb_days = int(nb_days)
        except ValueError:
            nb_days = DEFAULT_NB_DAYS
            _logger.info('It seems the ir.config_parameter(nb_days) '
                         'is not a valid number. DEFAULT_NB_DAYS=%s days '
                         'is used instead.' % DEFAULT_NB_DAYS)

        member_ids = self.search([('nb_days', '>=', nb_days)])
        partner_ids = member_ids.mapped('partner_id')

        partner_ids.signal_workflow('accept')

        return True
