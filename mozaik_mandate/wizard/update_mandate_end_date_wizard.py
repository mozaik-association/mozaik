# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_mandate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_mandate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_mandate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_mandate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT,\
    DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from datetime import datetime as dt


class abstract_update_mandate_end_date_wizard(orm.AbstractModel):
    _name = "abstract.update.mandate.end.date.wizard"

    _columns = {
        'mandate_end_date': fields.date('Mandate End Date',
                                        required=True,),
        'mandate_id': fields.many2one('abstract.mandate',
                                      string='Mandate',
                                      readonly=True),
        'message': fields.char(string="Message",
                               size=256,
                               readonly=True),
    }

    def default_get(self, cr, uid, flds, context):
        """
        To get default values for the object.
        """
        res = {}
        context = context or {}

        model = context.get('active_model', False)
        if not model:
            return res

        ids = context.get('active_ids') \
            or (context.get('active_id') and [context.get('active_id')]) \
            or []

        mandate = self.pool[model].browse(cr, uid, ids[0], context=context)

        res['mandate_end_date'] = dt.today().strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        res['mandate_id'] = mandate.id
        if mandate.active:
            res['message'] = _('Mandate will be invalidated'
                               ' by setting end date !')
        return res

    def set_mandate_end_date(self, cr, uid, ids, context=None):
        model = context.get('active_model', False)
        wizard = self.browse(cr, uid, ids, context=context)[0]
        if(dt.strptime(wizard.mandate_end_date,
                       DEFAULT_SERVER_DATE_FORMAT) >
           dt.strptime(fields.datetime.now(),
                       DEFAULT_SERVER_DATETIME_FORMAT)):
            raise orm.except_orm(_('Warning'),
                                 _('End date must be lower or'
                                   ' equal than today !'))
        vals = {}
        vals['end_date'] = wizard.mandate_end_date
        if wizard.mandate_id.active:
            self.pool[model].action_invalidate(cr,
                                               uid,
                                               wizard.mandate_id.id,
                                               context=context,
                                               vals=vals)
        else:
            self.pool[model].write(cr, uid, wizard.mandate_id.id,
                                   vals=vals, context=context)


class update_sta_mandate_end_date_wizard(orm.TransientModel):
    _name = "update.sta.mandate.end.date.wizard"
    _inherit = "abstract.update.mandate.end.date.wizard"

    _columns = {
        'mandate_end_date': fields.date('Mandate End Date',
                                        required=True,),
        'mandate_id': fields.many2one('sta.mandate',
                                      string='Mandate',
                                      readonly=True)
    }

    def set_mandate_end_date(self, cr, uid, ids, context=None):
        return super(update_sta_mandate_end_date_wizard,
                     self).set_mandate_end_date(cr, uid, ids, context=context)


class update_int_mandate_end_date_wizard(orm.TransientModel):
    _name = "update.int.mandate.end.date.wizard"
    _inherit = "abstract.update.mandate.end.date.wizard"

    _columns = {
        'mandate_end_date': fields.date('Mandate End Date',
                                        required=True,),
        'mandate_id': fields.many2one('int.mandate',
                                      string='Mandate',
                                      readonly=True)
    }

    def set_mandate_end_date(self, cr, uid, ids, context=None):
        return super(update_int_mandate_end_date_wizard,
                     self).set_mandate_end_date(cr, uid, ids, context=context)


class update_ext_mandate_end_date_wizard(orm.TransientModel):
    _name = "update.ext.mandate.end.date.wizard"
    _inherit = "abstract.update.mandate.end.date.wizard"

    _columns = {
        'mandate_end_date': fields.date('Mandate End Date',
                                        required=True,),
        'mandate_id': fields.many2one('ext.mandate',
                                      string='Mandate',
                                      readonly=True)
    }

    def set_mandate_end_date(self, cr, uid, ids, context=None):
        return super(update_ext_mandate_end_date_wizard,
                     self).set_mandate_end_date(
            cr, uid, ids, context=context)
