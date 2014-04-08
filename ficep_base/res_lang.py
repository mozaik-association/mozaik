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
from datetime import datetime
from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class lang(orm.Model):
    _inherit = 'res.lang'

    def _get_date_format(self, cr, uid, context):
        lang = context.get('lang')
        if not lang:
            lang = 'en_US'
        lang_id = self.search(cr, uid, [('code', '=', lang)], context=context)[0]
        return self.read(cr, uid, lang_id, ['date_format'])['date_format']

    def format_date(self, cr, uid, date_to_format, context):
        date_format = context.get('date_format')
        if not date_format:
            date_format = self._get_date_format(cr, uid, context)

        date_obj = datetime.strptime(date_to_format, DEFAULT_SERVER_DATE_FORMAT)
        return date_obj.strftime(date_format)
