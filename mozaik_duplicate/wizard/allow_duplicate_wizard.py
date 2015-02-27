# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_duplicate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_duplicate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_duplicate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_duplicate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp.tools.translate import _
from openerp.tools import SUPERUSER_ID

from openerp.addons.mozaik_duplicate.abstract_duplicate import \
    abstract_duplicate


MSG = {'generic.mandate': _('You must only select incompatible mandates!')}


class allow_duplicate_wizard(orm.TransientModel):

    _name = "allow.duplicate.wizard"

    def fields_view_get(
            self,
            cr,
            uid,
            view_id=None,
            view_type='form',
            context=None,
            toolbar=False,
            submenu=False):
        context = context or {}

        if not context.get('active_model', False):
            raise orm.except_orm(
                _('Error'),
                _('Missing active_model in context!'))

        multi_model = context.get('multi_model', False)
        model_id_name = context.get('model_id_name', False)

        if multi_model and not model_id_name:
            raise orm.except_orm(_('Error'), _('Missing model id key name!'))

        target_obj = self.pool[context.get('active_model')]
        discriminant_field = target_obj._discriminant_field
        document_ids = context.get('active_ids')

        documents = target_obj.browse(cr, uid, document_ids, context=context)
        discriminants = []
        for document in documents:
            if not document['is_duplicate_detected']:
                raise orm.except_orm(
                    _('Error'),
                    MSG.get(
                        context['active_model'],
                        _('You must only select duplicated entries!')))
            discriminants.append(document[discriminant_field])

        if len(set(discriminants)) != 1:
            raise orm.except_orm(
                _('Error'),
                _('You must select entries related to the same field "%s"!') %
                target_obj._columns[discriminant_field].string)

        if len(document_ids) == 1:
            discriminant = target_obj._is_discriminant_m2o(
            ) and discriminants[0].id or discriminants[0]
            domain_search = [(discriminant_field, '=', discriminant),
                             ('is_duplicate_allowed', '=', True)]
            allowed_document_ids = target_obj.search(
                cr,
                SUPERUSER_ID,
                domain_search,
                context=context)
            if not allowed_document_ids:
                raise orm.except_orm(
                    _('Error'),
                    _('You must select more than one entry!'))

        res = super(
            allow_duplicate_wizard,
            self).fields_view_get(
            cr,
            uid,
            view_id=view_id,
            view_type=view_type,
            context=context,
            toolbar=toolbar,
            submenu=submenu)
        return res

    def button_allow_duplicate(self, cr, uid, ids, context=None, vals=None):
        vals = vals or {}
        context = context or {}

        multi_model = context.get('multi_model', False)
        model_id_name = context.get('model_id_name', False)

        target_obj = self.pool[context.get('active_model')]
        document_ids = context.get('active_ids')

        if multi_model:
            current_values = target_obj.read(
                cr, uid, document_ids, [
                    'model', model_id_name], context=context)
            for value in current_values:
                values = dict(vals)
                model_obj = self.pool.get(value['model'])
                values.update(
                    model_obj.get_fields_to_update(
                        cr,
                        uid,
                        "allow",
                        context=context))
                super(
                    abstract_duplicate, model_obj).write(
                    cr, uid, [
                        value[model_id_name]], values, context=context)
        else:
            vals.update(
                target_obj.get_fields_to_update(
                    cr,
                    uid,
                    "allow",
                    context=context))
            target_obj.write(cr, uid, document_ids, vals, context=context)
