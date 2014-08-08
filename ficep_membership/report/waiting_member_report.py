# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
        'nb_days': fields.integer('Age')
    }

# orm methods

    def init(self, cr):
        """
        View that takes all partners where the status is into a
        one-month waiting acceptance since one month or more
        """
        tools.drop_view_if_exists(cr, 'waiting_member_report')
        cr.execute("""
            create or replace view waiting_member_report as (
                SELECT *
                FROM
                    (SELECT p.id as id,
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
                        membership_membership_line ml
                        ON ml.partner = p.id
                    WHERE
                        p.is_company = false AND
                        ml.is_current = true AND
                        ms.code = 'member_committee' OR
                        ms.code = 'former_member_committee'
                    ) as partner
            )
        """)

# public methods

    def process_accept_members(self, cr, uid, ids=None, context=None):
        """
        push the workflow for all
        found partner with the signal `accept`
        """
        nb_days = ''
        param_obj = self.pool['ir.config_parameter']
        param_ids = param_obj.\
            search(cr, uid, [('key', '=', 'nb_days')], context=context)
        if param_ids:
            nb_days = param_obj.read(
                cr, uid, param_ids, ['value'], context=context)[0]['value']

        try:
            nb_days = int(nb_days)
        except:
            nb_days = DEFAULT_NB_DAYS
            _logger.info("It seems that number of days is now a \
                string.DEFAULT_NB_DAYS(%s) is now used" % DEFAULT_NB_DAYS)
            pass

        if ids is None:
            ids = self.search(
                cr, uid, [('nb_days', '>', nb_days)], context=context)

        for waiting_member in self.browse(cr, uid, ids, context=context):
            waiting_member.partner_id.signal_workflow('accept')

        return True
