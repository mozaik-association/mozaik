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
import logging

from openerp.osv import orm
from openerp.tools import misc

_logger = logging.getLogger(__name__)


class ir_import(orm.TransientModel):

    _inherit = 'base_import.import'

# public methods

    def import_csv_file(self, cr, uid, args, context=None):
        """
        Import a CSV file from an xml file
        """
        context = context or {}
        context.update({
            'mail_create_nolog': True,
            'mail_notrack': True,
        })

        try:
            model = args[0]
            filename = args[1]
        except:
            _logger.error('Bad arguments: %s', args)
            return False

        try:
            fp = misc.file_open(filename)
            content = fp.read()
        except:
            _logger.error('Bad file name: %s', filename)
            return False

        fp.close()

        vals = {
            'res_model': model,
            'file': content,
            'file_name': filename,
            'file_type': 'application/vnd.ms-excel',
        }
        imp_id = self.create(cr, uid, vals, context=context)

        options = {
            'encoding': 'utf-8',
            'separator': ',',
            'headers': True,
            'quoting': '"',
        }
        preview = self.parse_preview(cr, uid, imp_id, options, context=context)
        fields = [f for f in preview['headers'] if not f.startswith('__dummy')]

        _logger.info('Importing file %s' % filename)
        res = self.do(cr, uid, imp_id, fields, options, context=context)
        if any(m['type'] == 'error' for m in res):
            _logger.error('Importing fails with following messages:')
            for m in res:
                _logger.error(m['message'])
        return res
