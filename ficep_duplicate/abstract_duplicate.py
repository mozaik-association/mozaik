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

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools.translate import _


class abstract_duplicate(orm.AbstractModel):

    _name = 'abstract.duplicate'
    # target model has to inherit from ['mail.thread']

    _discriminant_field = None
    _trigger_fileds = []
    _undo_redirect_action = None

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
                values.append(isinstance(discriminant[self._discriminant_field], tuple) and discriminant[self._discriminant_field][0] or discriminant[self._discriminant_field])
            self.detect_and_repair_duplicate(cr, SUPERUSER_ID, list(set(values)), context)
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        """
        =====
        write
        =====
        Override write method to detect and repair duplicates.
        """
        trigger_fields = (self._trigger_fileds or [self._discriminant_field]) + ['is_duplicate_detected', 'is_duplicate_allowed']
        updated_trigger_fields = [fld for fld in vals.keys() if fld in trigger_fields]
        if updated_trigger_fields:
            discriminants = self.read(cr, SUPERUSER_ID, ids, [self._discriminant_field], context=context)
        res = super(abstract_duplicate, self).write(cr, uid, ids, vals, context=context)
        if updated_trigger_fields:
            discriminants += self.read(cr, SUPERUSER_ID, ids, [self._discriminant_field], context=context)
            if discriminants:
                values = []
                for discriminant in discriminants:
                    values.append(isinstance(discriminant[self._discriminant_field], tuple) and discriminant[self._discriminant_field][0] or discriminant[self._discriminant_field])
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
                values.append(isinstance(discriminant[self._discriminant_field], tuple) and discriminant[self._discriminant_field][0] or discriminant[self._discriminant_field])
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
        self.write(cr, uid, ids,
                   {'is_duplicate_allowed': False}, context=context)

        # reload the tree with all duplicates
        duplicate = self.browse(cr, uid, ids, context=context)[0]
        value = isinstance(self._columns[self._discriminant_field], fields.many2one) and duplicate[self._discriminant_field].id or duplicate[self._discriminant_field]
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
        res = {}
        if mode == 'reset':
            return {'is_duplicate_detected': False,
                    'is_duplicate_allowed': False,
                   }
        if mode == 'duplicate':
            return {'is_duplicate_detected': True,
                    'is_duplicate_allowed': False,
                   }
        if mode == 'allow':
            return {'is_duplicate_detected': False,
                    'is_duplicate_allowed': True,
                   }

        raise orm.except_orm(_('ERROR'), _('Invalid mode: %s!') % mode)

    def detect_and_repair_duplicate(self, cr, uid, vals, context=None):
        """
        ===========================
        detect_and_repair_duplicate
        ===========================
        Detect automatically duplicates (setting the is_duplicate_detected flag)
        Repair orphan allowed or detected duplicate (resetting the corresponding flag)
        :param vals: discriminant values
        :type vals: list
        """
        for v in vals:
            document_ids = self.search(cr, uid, [(self._discriminant_field, '=', v)], context=context)
            if document_ids:
                current_values = self.read(cr, uid, document_ids, ['is_duplicate_allowed', 'is_duplicate_detected'], context=context)
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
                    if is_ok == 1:
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
                    super(abstract_duplicate, self).write(cr, uid, document_ids, fields_to_update, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
