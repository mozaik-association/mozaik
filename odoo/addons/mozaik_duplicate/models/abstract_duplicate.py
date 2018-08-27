# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import safe_eval


class AbstractDuplicate(models.AbstractModel):
    _name = 'abstract.duplicate'
    _inherit = ['mozaik.abstract.model']
    _description = "Abstract Duplicate Model"

    _discriminant_field = None
    _discriminant_model = None
    _reset_allowed = False
    _trigger_fields = []
    _undo_redirect_action = None

    is_duplicate_detected = fields.Boolean(
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )
    is_duplicate_allowed = fields.Boolean(
        readonly=True,
        copy=False,
    )

    @api.model
    def _is_discriminant_m2o(self):
        return isinstance(
            self._fields[self._discriminant_field], fields.Many2one)

    @api.model
    def _get_discriminant_model(self):
        if self._discriminant_model:
            return self.env.get(self._discriminant_model).browse()
        return self.browse()

    @api.multi
    def _get_discriminant_value(self, force_field=False):
        """
        Get the value of the discriminant field
        :param force_field: str
        :return: str, int, float, bool
        """
        self.ensure_one()
        if self._is_discriminant_m2o():
            force_field = force_field or 'id'
            value = self[self._discriminant_field]
            return value[force_field]
        return self[self._discriminant_field]

    @api.model
    def create(self, vals):
        """
        Override create method to detect and repair duplicates.
        :param vals: dict
        :return: self recordset
        """
        result = super().create(vals)
        if result:
            result = result.sudo()
            value = result._get_discriminant_value()
            self.suspend_security()._detect_and_repair_duplicate(value)
        return result

    @api.multi
    def write(self, vals):
        """
        Override write method to detect and repair duplicates.
        :param vals: dict
        :return: bool
        """
        trigger_fields = self._get_trigger_fields(vals.keys())
        detect = self and trigger_fields and \
            not self._context.get('escape_detection')
        if detect:
            self_suspend = self.suspend_security()
            values = [d._get_discriminant_value() for d in self_suspend]
        result = super().write(vals)
        if detect:
            values += [d._get_discriminant_value() for d in self_suspend]
            self_suspend._detect_and_repair_duplicate(values)
        return result

    def _get_trigger_fields(self, fields_list):
        """
        Get a list of fields who are into _trigger_fields and into given
        fields_list parameter (intersection).
        :param fields_list: list of str
        :return:
        """
        trigger_fields = self._trigger_fields or [self._discriminant_field]
        trigger_fields.extend([
            'is_duplicate_detected',
            'is_duplicate_allowed',
        ])
        return list(set(trigger_fields).intersection(fields_list))

    @api.multi
    def unlink(self):
        """
        Override unlink method to detect and repair duplicates.
        :return: bool
        """
        self_suspend = self.suspend_security()
        values = False
        if self:
            values = [d._get_discriminant_value() for d in self_suspend]
        result = super().unlink()
        if values:
            self_suspend._detect_and_repair_duplicate(values)
        return result

    @api.multi
    def button_undo_allow_duplicate(self):
        """
        Undo the effect of the "Allow duplicate" wizard.
        All allowed duplicates will be reset
        (see _detect_and_repair_duplicate).
        :return: dict
        """
        self.write({'is_duplicate_allowed': False})
        self.ensure_one()
        # Reload the tree with all duplicates
        value = self._get_discriminant_value()
        action = self.env.ref(self._undo_redirect_action).read()[0]
        # force the tree view
        action['view_mode'] = 'tree,' + action['view_mode'].replace(
            'tree,', '')
        action.pop('search_view', False)
        context = safe_eval(action["context"])
        context['search_default_%s' % self._discriminant_field] = value
        action.update({
            'context': context,
        })
        return action

    @api.model
    def _get_fields_to_update(self, mode):
        """
        Depending on a mode, builds a dictionary allowing to update duplicate
        fields
        :param mode: str
        :return: dict
        """
        result = super()._get_fields_to_update(mode)
        if mode in ['reset', 'deactivate']:
            result.update({
                'is_duplicate_detected': False,
                'is_duplicate_allowed': False,
            })
        elif mode == 'duplicate':
            result.update({
                'is_duplicate_detected': True,
                'is_duplicate_allowed': False,
            })
        elif mode == 'allow':
            result.update({
                'is_duplicate_detected': False,
                'is_duplicate_allowed': True,
            })
        return result

    @api.model
    def _get_duplicates(self, value):
        """
        Get duplicates
        :param value: str, int, float, bool
        :return: self recordset
        """
        result = self.browse()
        if self._discriminant_field:
            result = self.search([(self._discriminant_field, '=', value)])
        return result

    @api.model
    def _detect_and_repair_duplicate(self, values, columns_to_read=None):
        """
        Detect automatically duplicates (setting the is_duplicate_detected
        flag)
        Repair orphan allowed or detected duplicate (resetting the
        corresponding flag)
        :param values: list
        :param columns_to_read: list
        :return:
        """
        if not isinstance(values, list):
            values = [values]
        else:
            values = list(set(values))
        columns_to_read = columns_to_read or []
        columns_to_read.extend([
            'is_duplicate_allowed',
            'is_duplicate_detected',
        ])
        for value in values:
            duplicates = self._get_duplicates(value)
            values_write = {}
            if len(duplicates) > 1:
                val = {}
                nb_duplicates = len(duplicates.filtered(
                    lambda d: not d.is_duplicate_detected and
                    d.is_duplicate_allowed))
                if nb_duplicates == 1 or self._reset_allowed:
                    val.update({
                        'is_duplicate_allowed': False,
                    })
                nb_duplicates = len(duplicates.filtered(
                    lambda d: not d.is_duplicate_detected and not
                    d.is_duplicate_allowed))
                if nb_duplicates >= 1:
                    values_write = self._get_fields_to_update('duplicate')
            elif len(duplicates) == 1:
                if duplicates.is_duplicate_allowed or \
                        duplicates.is_duplicate_detected:
                    values_write = self._get_fields_to_update('reset')

            if values_write:
                # super write method must be called here to avoid to cycle
                if 'model' in columns_to_read:
                    super(AbstractDuplicate, duplicates).write(values_write)
                else:
                    duplicates.write(values_write)
        return True
