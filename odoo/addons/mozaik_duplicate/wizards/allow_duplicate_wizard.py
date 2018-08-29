# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, models, _


class AllowDuplicateWizard(models.TransientModel):
    _name = "allow.duplicate.wizard"
    _description = "Allow duplicates wizard"

    @api.model
    def view_init(self, fields_list):
        """
        Overwrite this function to check if the wizard can be called
        (with correct information).
        :return: dict
        """
        context = self.env.context
        active_model = context.get('active_model', False)
        if not active_model:
            raise exceptions.MissingError(
                _('Missing active_model in context!'))
        target_obj = self.env[active_model]
        discriminant_field = target_obj._discriminant_field
        active_ids = context.get('active_ids')
        targets = target_obj.browse(active_ids)
        if targets.filtered(lambda t: not t.is_duplicate_detected):
            message = self.get_error_msg_by_model(active_model)
            raise exceptions.UserError(message)
        discriminants = [t._get_discriminant_value() for t in targets]

        if len(set(discriminants)) != 1:
            message = _('You must select entries related to the same field '
                        '"%s"!') % discriminant_field
            raise exceptions.UserError(message)

        if len(active_ids) == 1:
            # We have only 1 value
            discriminant = discriminants[0]
            domain_search = [
                (discriminant_field, '=', discriminant),
                ('is_duplicate_allowed', '=', True),
            ]
            if not target_obj.search_count(domain_search):
                raise exceptions.UserError(
                    _('You must select more than one entry!'))
        return super().view_init(fields_list)

    @api.model
    def get_error_msg_by_model(self, model):
        """
        Based on the given model, get the specific error message.
        If no specific messages, the default one is returned.
        Useful for inheritance (because this model is abstract)
        :param model: str
        :return: str
        """
        return _('You must only select duplicated entries!')

    @api.multi
    def button_allow_duplicate(self, vals=None):
        """
        Button/action to allow duplicates
        :return: dict
        """
        vals = vals or {}
        context = self.env.context
        multi_model = context.get('multi_model')
        model_id_name = context.get('model_id_name')
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        target_obj = self.env[active_model]
        targets = target_obj.browse(active_ids)
        if multi_model:
            for target in targets:
                model_id_name_value = target[model_id_name]
                model_obj = self.env[target.model]
                values = model_obj._get_fields_to_update("allow")
                vals.update(values)
                model_id_name_value.write(vals)
        else:
            values = target_obj._get_fields_to_update("allow")
            vals.update(values)
            targets.write(vals)
