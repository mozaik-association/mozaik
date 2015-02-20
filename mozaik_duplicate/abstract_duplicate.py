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

from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID


class abstract_duplicate(orm.AbstractModel):

    _name = 'abstract.duplicate'
    _inherit = ['mozaik.abstract.model']
    _description = "Abstract Duplicate"

    _discriminant_field = None
    _discriminant_model = None
    _reset_allowed = False
    _trigger_fields = []
    _undo_redirect_action = None

# private methods

    def _is_discriminant_m2o(self):
        return isinstance(self._columns[self._discriminant_field], fields.many2one)

    def _get_discriminant_model(self):
        if not self._discriminant_model:
            return self
        else:
            return self.pool.get(self._discriminant_model)
# fields

    _columns = {
        # Duplicates
        'is_duplicate_detected': fields.boolean('Is Duplicate Detected', readonly=True),
        'is_duplicate_allowed': fields.boolean('Is Duplicate Allowed', readonly=True, track_visibility='onchange'),
    }

# orm methods

    def create(self, cr, uid, vals, context=None):
        """
        ======
        create
        ======
        Override create method to detect and repair duplicates.
        :rparam: id of the new document
        :rtype: integer
        """
        new_id = super(abstract_duplicate, self).create(cr, uid, vals, context=context)
        # check new duplicate state after creation
        discriminants = self.read(cr, SUPERUSER_ID, [new_id], [self._discriminant_field], context=context)
        if discriminants:
            values = []
            for discriminant in discriminants:
                values.append(self._is_discriminant_m2o() and discriminant[self._discriminant_field][0] or discriminant[self._discriminant_field])
            self.detect_and_repair_duplicate(cr, SUPERUSER_ID, list(set(values)), context)
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        """
        =====
        write
        =====
        Override write method to detect and repair duplicates.
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        trigger_fields = (self._trigger_fields or [self._discriminant_field]) + ['is_duplicate_detected', 'is_duplicate_allowed']
        updated_trigger_fields = [fld for fld in vals.keys() if fld in trigger_fields]
        if updated_trigger_fields:
            discriminants = self.read(cr, SUPERUSER_ID, ids, [self._discriminant_field], context=context)
        res = super(abstract_duplicate, self).write(cr, uid, ids, vals, context=context)
        if updated_trigger_fields:
            discriminants += self.read(cr, SUPERUSER_ID, ids, [self._discriminant_field], context=context)
            if discriminants:
                values = []
                for discriminant in discriminants:
                    values.append(self._is_discriminant_m2o() and discriminant[self._discriminant_field][0] or discriminant[self._discriminant_field])
                self.detect_and_repair_duplicate(cr, SUPERUSER_ID, list(set(values)), context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        """
        ======
        unlink
        ======
        Override unlink method to detect and repair duplicates.
        """
        discriminants = self.read(cr, SUPERUSER_ID, ids, [self._discriminant_field], context=context)
        res = super(abstract_duplicate, self).unlink(cr, uid, ids, context=context)
        if discriminants:
            values = []
            for discriminant in discriminants:
                values.append(self._is_discriminant_m2o() and discriminant[self._discriminant_field][0] or discriminant[self._discriminant_field])
            self.detect_and_repair_duplicate(cr, SUPERUSER_ID, list(set(values)), context)
        return res

# view methods: onchange, button

    def button_undo_allow_duplicate(self, cr, uid, ids, context=None):
        """
        ===========================
        button_undo_allow_duplicate
        ===========================
        Undo the effect of the "Allow duplicate" wizard
        :rparam: True
        :rtype: boolean

        **Note**
        All allowed duplicates will be reset
        (see detect_and_repair_duplicate)
        """
        ids = isinstance(ids, (long, int)) and [ids] or ids
        self.write(cr, uid, ids,
                   {'is_duplicate_allowed': False}, context=context)
        if len(ids) != 1:
            return True

        # reload the tree with all duplicates
        duplicate = self.browse(cr, uid, ids, context=context)[0]
        value = self._is_discriminant_m2o() and duplicate[self._discriminant_field].id or duplicate[self._discriminant_field]
        action_name = self._undo_redirect_action.split('.', 1)
        action = self.pool['ir.actions.act_window'].for_xml_id(cr, uid, action_name[0], action_name[1], context=context)
        action.pop('search_view')
        ctx = action.get('context') and eval(action['context']) or {}
        ctx.update({'search_default_%s' % self._discriminant_field: value})
        action['context'] = str(ctx)

        return action

# public methods

    def get_fields_to_update(self, cr, uid, mode, context=None):
        """
        ====================
        get_fields_to_update
        ====================
        Depending on a mode, builds a dictionary allowing to update duplicate fields
        :rparam: fields to update
        :rtype: dictionary
        """
        res = super(abstract_duplicate, self).get_fields_to_update(cr, uid, mode, context=context)
        if mode in ['reset', 'deactivate']:
            res.update({
                'is_duplicate_detected': False,
                'is_duplicate_allowed': False,
            })
        if mode == 'duplicate':
            res.update({
                'is_duplicate_detected': True,
                'is_duplicate_allowed': False,
            })
        if mode == 'allow':
            res.update({
                'is_duplicate_detected': False,
                'is_duplicate_allowed': True,
            })
        return res

    def get_duplicate_ids(self, cr, uid, value, context=None):
        return [], self.search(cr, uid, [(self._discriminant_field, '=', value)], context=context)

    def detect_and_repair_duplicate(self, cr, uid, vals, context=None, columns_to_read=None, model_id_name=None):
        """
        ===========================
        detect_and_repair_duplicate
        ===========================
        Detect automatically duplicates (setting the is_duplicate_detected flag)
        Repair orphan allowed or detected duplicate (resetting the corresponding flag)
        :param vals: discriminant values
        :param detection_model: model use to detect duplicates
        :param columns_to_read: columns to read in detection model
        :param model_id_name: name of id column of model
        :type vals: list
        """
        columns_to_read = columns_to_read or []
        columns_to_read.extend(['is_duplicate_allowed', 'is_duplicate_detected'])

        for v in vals:
            document_to_reset_ids, document_ids = self.get_duplicate_ids(cr, uid, v, context=None)
            if document_ids:
                current_values = self._get_discriminant_model().read(cr, uid, document_ids, columns_to_read, context=context)
                fields_to_update = {}
                if len(document_ids) > 1:
                    is_ok = 0
                    val = {}
                    for value in current_values:
                        if not value['is_duplicate_detected'] and value['is_duplicate_allowed']:
                            is_ok += 1
                            val = value
                            if is_ok == 2:
                                break
                    if is_ok == 1 or self._reset_allowed:
                        val['is_duplicate_allowed'] = False

                    is_ok = 0
                    for value in current_values:
                        if not value['is_duplicate_detected'] and not value['is_duplicate_allowed']:
                            is_ok += 1
                            break
                    if is_ok >= 1:
                        fields_to_update = self.get_fields_to_update(cr, uid, 'duplicate', context=None)
                else:
                    if current_values[0]['is_duplicate_allowed'] or current_values[0]['is_duplicate_detected']:
                        fields_to_update = self.get_fields_to_update(cr, uid, 'reset', context=None)

                if fields_to_update:
                    # super write method must be called here to avoid to cycle
                    if 'model' in columns_to_read:
                        for value in current_values:
                            super(abstract_duplicate, self.pool.get(value['model'])).write(cr, uid, [value[model_id_name]], fields_to_update, context=context)
                    else:
                        super(abstract_duplicate, self).write(cr, uid, document_ids, fields_to_update, context=context)

            if document_to_reset_ids:
                fields_to_update = self.get_fields_to_update(cr, uid, 'reset', context=None)
                if 'model' in columns_to_read:
                    current_values = self._get_discriminant_model().read(cr, uid, document_to_reset_ids, ['model', model_id_name], context=context)
                    for value in current_values:
                        super(abstract_duplicate, self.pool.get(value['model'])).write(cr, uid, [value[model_id_name]], fields_to_update, context=context)
                else:
                    super(abstract_duplicate, self).write(cr, uid, document_to_reset_ids, fields_to_update, context=context)

