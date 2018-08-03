# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AbstractDuplicate(models.Model):

    _name = 'abstract.duplicate'
    _inherit = ['mozaik.abstract.model']
    _description = "Abstract Duplicate"

    _discriminant_field = None
    _discriminant_model = None
    _reset_allowed = False
    _trigger_fields = []
    _undo_redirect_action = None

    # private methods
    @api.model
    def _is_discriminant_m2o(self):
        return isinstance(
            self._fields[self._discriminant_field], fields.Many2one)

    @api.model
    def _get_discriminant_model(self):
        if not self._discriminant_model:
            return self
        else:
            return self.env.get(self._discriminant_model)

    # fields
    is_duplicate_detected = fields.Boolean('Is Duplicate Detected',
                                           readonly=True)
    is_duplicate_allowed = fields.Boolean('Is Duplicate Allowed',
                                          readonly=True,
                                          track_visibility='onchange')

    # orm methods
    @api.model
    def create(self, vals):
        """
        ======
        create
        ======
        Override create method to detect and repair duplicates.
        :rparam: id of the new document
        :rtype: integer
        """
        # TODO sudo
        discriminants = super(AbstractDuplicate, self.sudo()).create(vals)
        if discriminants:
            values = []
            for discriminant in discriminants:
                values.append(self._is_discriminant_m2o() and
                              discriminant[self._discriminant_field].id or
                              discriminant[self._discriminant_field])
            self.detect_and_repair_duplicate(list(set(values)))
        return discriminants

    @api.multi
    def write(self, vals):
        """
        =====
        write
        =====
        Override write method to detect and repair duplicates.
        """
        self_sudo = self.sudo()  # TODO
        trigger_fields = ((self._trigger_fields or [self._discriminant_field])
                          + ['is_duplicate_detected', 'is_duplicate_allowed'])
        updated_trigger_fields = [
            fld for fld in vals.keys() if fld in trigger_fields]
        if updated_trigger_fields:
            discriminants = self_sudo.read([self._discriminant_field])
        res = super().write(vals)
        if updated_trigger_fields:
            discriminants += self_sudo.read([self._discriminant_field])
            if discriminants:
                values = []
                for discriminant in discriminants:
                    values.append(
                        self._is_discriminant_m2o() and
                        discriminant[self._discriminant_field][0] or
                        discriminant[self._discriminant_field])
                self_sudo.detect_and_repair_duplicate(list(set(values)))
        return res

    @api.multi
    def unlink(self):
        """
        ======
        unlink
        ======
        Override unlink method to detect and repair duplicates.
        """
        self_sudo = self.sudo()
        discriminants = self_sudo.read([self._discriminant_field])
        res = super().unlink()
        if discriminants:
            values = []
            for discriminant in discriminants:
                values.append(
                    self._is_discriminant_m2o() and
                    discriminant[self._discriminant_field][0] or
                    discriminant[self._discriminant_field])
            self.detect_and_repair_duplicate(list(set(values)))
        return res

    # view methods: onchange, button
    @api.multi
    def button_undo_allow_duplicate(self):
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
        self.write({'is_duplicate_allowed': False})
        if len(self) != 1:
            return True

        # reload the tree with all duplicates
        value = (self._is_discriminant_m2o() and
                 self[self._discriminant_field].id or
                 self[self._discriminant_field])
        action_name = self._undo_redirect_action.split('.', 1)
        action = self.pool['ir.actions.act_window'].for_xml_id(
            action_name[0], action_name[1])
        action.pop('search_view')
        ctx = action.get('context') and eval(action['context']) or {}
        ctx.update({'search_default_%s' % self._discriminant_field: value})
        action['context'] = str(ctx)

        return action

    # public methods
    @api.model
    def get_fields_to_update(self, mode):
        """
        ====================
        get_fields_to_update
        ====================
        Depending on a mode, builds a dictionary allowing to update duplicate
        fields
        :rparam: fields to update
        :rtype: dictionary
        """
        res = super().get_fields_to_update(mode)
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

    @api.model
    def get_duplicate_ids(self, value):
        return [], self.search([(self._discriminant_field, '=', value)])

    @api.model
    def detect_and_repair_duplicate(self, vals,
                                    columns_to_read=None, model_id_name=None):
        """
        ===========================
        detect_and_repair_duplicate
        ===========================
        Detect automatically duplicates (setting the is_duplicate_detected
        flag)
        Repair orphan allowed or detected duplicate (resetting the
        corresponding flag)
        :param vals: discriminant values
        :param detection_model: model use to detect duplicates
        :param columns_to_read: columns to read in detection model
        :param model_id_name: name of id column of model
        :type vals: list
        """
        columns_to_read = columns_to_read or []
        columns_to_read.extend(['is_duplicate_allowed',
                                'is_duplicate_detected'])

        for v in vals:
            document_to_reset_ids, document_ids = self.get_duplicate_ids(v)
            if document_ids:
                fields_to_update = {}
                if len(document_ids) > 1:
                    is_ok = 0
                    val = {}
                    for value in document_ids:
                        if not value.is_duplicate_detected and \
                                value.is_duplicate_allowed:
                            is_ok += 1
                            val = value
                            if is_ok == 2:
                                break
                    if is_ok == 1 or self._reset_allowed:
                        val['is_duplicate_allowed'] = False

                    is_ok = 0
                    for value in document_ids:
                        if not value.is_duplicate_detected and \
                                not value.is_duplicate_allowed:
                            is_ok += 1
                            break
                    if is_ok >= 1:
                        fields_to_update = self.get_fields_to_update(
                            'duplicate')
                else:
                    if document_ids.is_duplicate_allowed or \
                            document_ids.is_duplicate_detected:
                        fields_to_update = self.get_fields_to_update('reset')

                if fields_to_update:
                    # super write method must be called here to avoid to cycle
                    if 'model' in columns_to_read:
                        for value in document_ids:
                            super(AbstractDuplicate, value).write(
                                fields_to_update)
                    else:
                        document_ids.write(fields_to_update)

            if document_to_reset_ids:
                fields_to_update = self.get_fields_to_update(
                    'reset')
                if 'model' in columns_to_read:
                    current_values = self._get_discriminant_model().read(
                        document_to_reset_ids,
                        ['model', model_id_name])
                    for value in current_values:
                        super(AbstractDuplicate,
                              self.env.get(value['model'])).write(
                            [value[model_id_name]],
                            fields_to_update)
                else:
                    super().write(fields_to_update)
