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
from openerp.tools.translate import _


class abstract_update_mandate_end_date_wizard(orm.AbstractModel):
    _name = "abstract.update.mandate.end.date.wizard"

    _columns = {
        'mandate_end_date': fields.date('Mandate End Date'),
        'mandate_deadline_date': fields.date('Mandate Deadline Date'),
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

        mode = context.get('mode', 'end_date')

        model = context.get('active_model', False)
        if not model:
            return res

        ids = context.get('active_ids') \
            or (context.get('active_id') and [context.get('active_id')]) \
            or []

        mandate = self.pool[model].browse(cr, uid, ids[0], context=context)
        res['mandate_id'] = mandate.id

        if mode == 'end_date':
            res['mandate_end_date'] = fields.date.today()

            if mandate.active:
                res['message'] = _('Mandate will be invalidated'
                                   ' by setting end date !')
        elif mode == 'reactivate':
            if mandate.active:
                res['message'] = _('The selected mandate is already active!')
            if not mandate.mandate_category_id.active:
                res['message'] = _('The mandate category is not active'
                                   ' anymore!')
            if mandate.designation_int_assembly_id and \
                    not mandate.designation_int_assembly_id.active:
                res['message'] = _('The designation assembly is not active'
                                   ' anymore!')
            if not mandate.partner_id.active:
                res['message'] = _('The representative is not active'
                                   ' anymore!')
        return res

    def set_mandate_end_date(self, cr, uid, ids, context=None):
        model = context.get('active_model', False)
        wizard = self.browse(cr, uid, ids, context=context)[0]
        if wizard.mandate_end_date > fields.date.today():
            raise orm.except_orm(
                _('Warning'),
                _('End date must be lower or equal than today!'))
        if wizard.mandate_end_date > wizard.mandate_id.deadline_date:
            raise orm.except_orm(
                _('Warning'),
                _('End date must be lower or equal than deadline date!'))
        if wizard.mandate_id.start_date > wizard.mandate_end_date:
            raise orm.except_orm(
                _('Warning'),
                _('End date must be greater or equal than start date!'))
        vals = {'end_date': wizard.mandate_end_date}
        if wizard.mandate_id.active:
            self.pool[model].action_invalidate(cr,
                                               uid,
                                               [wizard.mandate_id.id],
                                               context=context,
                                               vals=vals)
        else:
            self.pool[model].write(cr, uid, wizard.mandate_id.id,
                                   vals=vals, context=context)

    def reactivate_mandate(self, cr, uid, ids, context=None):
        model = context.get('active_model', False)
        wizard = self.browse(cr, uid, ids, context=context)[0]
        if wizard.mandate_deadline_date <= fields.date.today():
            raise orm.except_orm(
                _('Warning'),
                _('New deadline date must be greater than today !'))

        vals = {
            'deadline_date': wizard.mandate_deadline_date,
            'end_date': False,
        }

        if wizard.mandate_id.postal_coordinate_id and \
                not wizard.mandate_id.postal_coordinate_id.active:
            vals['postal_coordinate_id'] = False

        if wizard.mandate_id.email_coordinate_id and \
                not wizard.mandate_id.email_coordinate_id.active:
            vals['email_coordinate_id'] = False

        self.pool[model].action_revalidate(
            cr, uid, wizard.mandate_id.id, vals=vals, context=context)


class update_sta_mandate_end_date_wizard(orm.TransientModel):
    _name = "update.sta.mandate.end.date.wizard"
    _inherit = "abstract.update.mandate.end.date.wizard"

    _columns = {
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
        'mandate_id': fields.many2one('int.mandate',
                                      string='Mandate',
                                      readonly=True)
    }

    def default_get(self, cr, uid, flds, context):
        """
        To get default values for the object.
        """
        context = context or {}
        res = super(update_int_mandate_end_date_wizard, self).default_get(
            cr, uid, flds=flds, context=context)

        if res.get('message', False):
            return res

        mode = context.get('mode', 'end_date')

        model = context.get('active_model', False)
        if not model:
            return res

        ids = context.get('active_ids') \
            or (context.get('active_id') and [context.get('active_id')]) \
            or []

        mandate = self.pool[model].browse(cr, uid, ids[0], context=context)

        if mode == 'reactivate':
            if not mandate.int_assembly_id.active:
                res['message'] = _('The assembly is not active'
                                   ' anymore!')
        return res

    def set_mandate_end_date(self, cr, uid, ids, context=None):
        return super(update_int_mandate_end_date_wizard,
                     self).set_mandate_end_date(cr, uid, ids, context=context)


class update_ext_mandate_end_date_wizard(orm.TransientModel):
    _name = "update.ext.mandate.end.date.wizard"
    _inherit = "abstract.update.mandate.end.date.wizard"

    _columns = {
        'mandate_id': fields.many2one('ext.mandate',
                                      string='Mandate',
                                      readonly=True)
    }

    def default_get(self, cr, uid, flds, context):
        """
        To get default values for the object.
        """
        context = context or {}
        res = super(update_ext_mandate_end_date_wizard, self).default_get(
            cr, uid, flds=flds, context=context)

        if res.get('message', False):
            return res

        mode = context.get('mode', 'end_date')

        model = context.get('active_model', False)
        if not model:
            return res

        ids = context.get('active_ids') \
            or (context.get('active_id') and [context.get('active_id')]) \
            or []

        mandate = self.pool[model].browse(cr, uid, ids[0], context=context)

        if mode == 'reactivate':
            if not mandate.ext_assembly_id.active:
                res['message'] = _('The assembly is not active'
                                   ' anymore!')
        return res

    def set_mandate_end_date(self, cr, uid, ids, context=None):
        return super(update_ext_mandate_end_date_wizard,
                     self).set_mandate_end_date(
            cr, uid, ids, context=context)
