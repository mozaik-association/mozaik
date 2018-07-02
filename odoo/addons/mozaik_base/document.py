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

import sys

from openerp.osv import orm

WIN = sys.platform.startswith('win')


class document_file(orm.Model):

    _inherit = 'ir.attachment'

    def _index(self, cr, uid, data, datas_fname, file_type):
        '''
        Under Windows try to avoid the doIndex crash when executing
        the `file´ Unix command
        '''
        if not WIN or datas_fname or file_type:
            res = super(document_file, self)._index(
                cr, uid, data, datas_fname, file_type)
            return res

        return None, None
