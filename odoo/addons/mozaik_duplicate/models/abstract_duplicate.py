# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AbstractDuplicate(models.AbstractModel):
    _name = 'abstract.duplicate'
    _inherit = ['mozaik.abstract.model']
    _description = "Abstract Duplicate"

    _discriminant_field = None
    _discriminant_model = None
    _reset_allowed = False
    _trigger_fields = []
    _undo_redirect_action = None

    is_duplicate_detected = fields.Boolean(
        readonly=True,
    )
    is_duplicate_allowed = fields.Boolean(
        readonly=True,
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
    def _get_discriminant_value(self):
        """
        Get the value of the discriminant field
        :return: str, int, float, bool
        """
        self.ensure_one()
        if self._is_discriminant_m2o():
            return self[self._discriminant_field].id
        return self[self._discriminant_field]

    @api.model
    def create(self, vals):
        """
        Override create method to detect and repair duplicates.
        :param vals: dict
        :return: self recordset
        """
        result = super(AbstractDuplicate, self.sudo()).create(vals)
        if result:
            value = result._get_discriminant_value()
            self.detect_and_repair_duplicate(value)
        return result

    @api.multi
    def write(self, vals):
        """
        Override write method to detect and repair duplicates.
        :param vals: dict
        :return: bool
        """
        self_sudo = self.sudo()
        trigger_fields = self._trigger_fields or [self._discriminant_field]
        trigger_fields.extend([
            'is_duplicate_detected',
            'is_duplicate_allowed',
        ])
        updated_trigger_fields = [
            fld for fld in vals.keys() if fld in trigger_fields]
        result = super(AbstractDuplicate, self).write(vals)
        if self and updated_trigger_fields:
            values = [d._get_discriminant_value() for d in self_sudo]
            self_sudo.detect_and_repair_duplicate(values)
        return result

    @api.multi
    def unlink(self):
        """
        Override unlink method to detect and repair duplicates.
        :return: bool
        """
        self_sudo = self.sudo()
        result = super(AbstractDuplicate, self).unlink()
        if self:
            values = [d._get_discriminant_value() for d in self_sudo]
            self.detect_and_repair_duplicate(values)
        return result

    @api.multi
    def button_undo_allow_duplicate(self):
        """
        Undo the effect of the "Allow duplicate" wizard.
        All allowed duplicates will be reset (see detect_and_repair_duplicate).
        :return: dict
        """
        self.write({'is_duplicate_allowed': False})
        if len(self) != 1:
            return {}
        # Reload the tree with all duplicates
        value = self._get_discriminant_value()
        action = self.env.ref(self._undo_redirect_action).read()[0]
        action.pop('search_view', False)
        context = {
            'search_default_%s' % self._discriminant_field: value,
        }
        action.update({
            'context': context,
        })
        return action

    @api.model
    def get_fields_to_update(self, mode):
        """
        Depending on a mode, builds a dictionary allowing to update duplicate
        fields
        :param mode: str
        :return: dict
        """
        result = super(AbstractDuplicate, self).get_fields_to_update(mode)
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
    def get_duplicates(self, value):
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
    def detect_and_repair_duplicate(self, values, columns_to_read=None):
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
            duplicates = self.get_duplicates(value)
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
                    values_write = self.get_fields_to_update('duplicate')
            elif len(duplicates) == 1:
                if duplicates.is_duplicate_allowed or \
                        duplicates.is_duplicate_detected:
                    values_write = self.get_fields_to_update('reset')

            if values_write:
                # super write method must be called here to avoid to cycle
                if 'model' in columns_to_read:
                    super(AbstractDuplicate, duplicates).write(values_write)
                else:
                    duplicates.write(values_write)
        return True
