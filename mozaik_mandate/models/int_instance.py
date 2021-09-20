# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class IntInstance(models.Model):

    _inherit = 'int.instance'

    def _get_model_ids(self, model):
        """
        Get all ids for a given model that are linked to an designation
        assembly for the current instance
        :type model: char
        :param model: model is the name of the model to make the search
        :rtype: [integer]
        :rparam: list of ids for the model `model`.
        """
        self.ensure_one()
        assembly_obj = self.env['int.assembly']
        model_obj = self.env[model]
        domain = [
            ('instance_id', '=', self.id),
            ('is_designation_assembly', '=', True)
        ]
        assembly_ids = assembly_obj.search(domain).ids
        domain = [
            ('designation_int_assembly_id', 'in', assembly_ids),
        ]
        res_ids = model_obj.search(domain).ids
        return res_ids

    def get_model_action(self):
        """
        return an action for a specific model contains into the context
        """
        self.ensure_one()
        context = self.env.context
        action =\
            context.get('action') and context.get('action').split('.') or []
        if not len(action) == 2:
            raise Warning(
                _('A model and an action for this model are required for '
                  'this operation'))

        module = action[0]
        action_name = action[1]
        # get model's action to update its domain
        action = self.env['ir.actions.act_window'].for_xml_id(
            module, action_name)
        model = action['res_model']
        res_ids = self._get_model_ids(model)
        domain = [('id', 'in', res_ids)]
        action['domain'] = domain
        return action

    def _compute_mandate_count(self):
        """
        This method will set the value for
        * sta_mandate_count
        * ext_mandate_count
        * int_mandate_count
        """
        for inst in self:
            inst.ext_mandate_count = len(inst._get_model_ids('ext.mandate'))
            inst.int_mandate_count = len(inst._get_model_ids('int.mandate'))
            inst.sta_mandate_count = len(inst._get_model_ids('sta.mandate'))

    sta_mandate_count = fields.Integer(
        compute='_compute_mandate_count',
        string='State Mandates')
    ext_mandate_count = fields.Integer(
        compute='_compute_mandate_count',
        string='External Mandates')
    int_mandate_count = fields.Integer(
        compute='_compute_mandate_count',
        string='Internal Mandates')
