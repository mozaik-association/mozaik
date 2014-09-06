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
from openerp.osv import orm


class email_coordinate(orm.Model):

    def _get_linked_mailing(self, cr, uid, ids, context=None):
        '''
        :rtype: [integer]
        :rparam: list of `mail.mass_mailing.contact` associated with a partner
            id into `ids`
        '''
        mailing_ids = []
        partner_ids = self.get_linked_partners(cr, uid, ids, context=context)
        if partner_ids:
            mailing_ids = self.pool['mail.mass_mailing.contact'].search(
                cr, uid, [('partner_id', 'in', partner_ids)], context=context)
        return mailing_ids

    _inherit = 'email.coordinate'
