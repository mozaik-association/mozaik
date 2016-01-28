# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from openerp import tools
from openerp.osv import orm, fields

DEFAULT_NB_DAYS = 30
_logger = logging.getLogger(__name__)


class waiting_member_report(orm.Model):

    _name = "waiting.member.report"
    _description = 'Members Committee'
    _auto = False

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Natural Persons'),
        'identifier': fields.integer('Identifier'),
        'membership_state_id': fields.many2one('membership.state',
                                               'Membership State'),
        'nb_days': fields.integer('#Days')
    }

    _order = "nb_days desc, partner_id"

# orm methods

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

# public methods

    def process_accept_members(self, cr, uid, ids=None, context=None):
        """
        Advance the workflow with the signal `accept`
        for all partners found
        """
        nb_days = self.pool['ir.config_parameter'].get_param(
            cr, uid, 'nb_days', default=DEFAULT_NB_DAYS, context=context)

        try:
            nb_days = int(nb_days)
        except:
            nb_days = DEFAULT_NB_DAYS
            _logger.info('It seems the ir.config_parameter(nb_days) '
                         'is not a valid number. DEFAULT_NB_DAYS=%s days '
                         'is used instead.' % DEFAULT_NB_DAYS)

        ids = self.search(
            cr, uid, [('nb_days', '>=', nb_days)], context=context)

        pids = [
            pid['id']
            for pid in self.read(cr, uid, ids, ['partner_id'], context=context)
        ]

        self.pool['res.partner'].signal_workflow(
            cr, uid, set(pids), 'accept', context=context)

        return True
