# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class UpdateExtMandateEndDateWizard(models.TransientModel):

    _inherit = "abstract.update.mandate.end.date.wizard"
    _name = "update.ext.mandate.end.date.wizard"

    mandate_id = fields.Many2one(
        comodel_name='ext.mandate',
        string='Mandate',
        readonly=True)

    @api.model
    def default_get(self, fields_list):
        """
        To get default values for the object.
        """
        context = self.env.context or {}
        res = super().default_get(fields_list)

        if res.get('message', False):
            return res

        mode = context.get('mode', 'end_date')

        model = context.get('active_model', False)
        if not model:
            return res

        ids = context.get('active_ids') \
            or (context.get('active_id') and [context.get('active_id')]) \
            or []

        mandate = self.env[model].browse(ids[0])

        if mode == 'reactivate':
            if not mandate.ext_assembly_id.active:
                res['message'] = _('The assembly is not active'
                                   ' anymore!')
        return res
