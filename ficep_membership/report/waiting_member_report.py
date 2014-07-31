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
from openerp import tools
from openerp.osv import orm, fields


class waiting_member_report(orm.Model):

    _name = "waiting.member.report"
    _description = 'Waiting Member Report'
    _auto = False

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Natural Persons'),
        'membership_state_id': fields.many2one('membership.state', 'Membership State'),
        'one_month': fields.float('One Month')
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
                            ms.id as membership_state_id,
                            EXTRACT
                                (year FROM age(ml.date_from))*12 +
                            EXTRACT
                                (month FROM age(ml.date_from)) +
                            EXTRACT
                                (day FROM age(ml.date_from))/30 AS
                            one_month
                    FROM res_partner p
                    JOIN membership_state ms
                        ON ms.id = p.membership_state_id
                    JOIN
                        membership_membership_line ml
                        ON ml.partner = p.id
                    WHERE
                        p.is_company = false AND
                        ms.code = 'future_commitee_member' AND
                        ml.is_current = true
                    ) as partner
                WHERE one_month >= 1
            )
        """)
# public methods

    def process_accept_members(self, cr, uid, ids=None, context=None):
        """
        ======================
        process_accept_members
        ======================
        push the workflow for all
        found partner with the signal `accept`
        """
        if ids is None:
            ids = self.search(cr, uid, [], context=context)
        for waiting_member in self.browse(cr, uid, ids, context=context):
            waiting_member.partner_id.signal_workflow('accept')
        return True
