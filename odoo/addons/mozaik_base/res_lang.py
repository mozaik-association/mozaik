# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_base, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_base is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_base is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_base.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class lang(orm.Model):

    _inherit = 'res.lang'

    def _get_default_date_format(self, cursor, user, context=None):
        '''
        Use as default date format the european format
        '''
        return '%d/%m/%Y'

    def _get_date_format(self, cr, uid, context):
        lang = context.get('lang')
        if not lang:
            lang = 'en_US'
        lang_id = self.search(
            cr, uid, [('code', '=', lang)], context=context)[0]
        return self.read(cr, uid, lang_id, ['date_format'])['date_format']

    def format_date(self, cr, uid, date_to_format, context):
        date_format = context.get('date_format')
        if not date_format:
            date_format = self._get_date_format(cr, uid, context)

        date_obj = datetime.strptime(
            date_to_format, DEFAULT_SERVER_DATE_FORMAT)
        return date_obj.strftime(date_format)
