# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class IrUiView(models.Model):

    _inherit = 'ir.ui.view'

    @api.model
    def default_view(self, model, view_type):
        """ Get the default view for the provided (model, view_type) pair:
        if native method returns nothing try to search without the condition
        'mode==primary', maybe a view based on a primary abstract view exists

        :param str model:
        :param int view_type:
        :return: id of the default view of False if none found
        :rtype: int
        """
        view_id = super().default_view(model, view_type)
        if not view_id:
            domain = [('model', '=', model), ('type', '=', view_type)]
            view_id = self.search(domain, limit=1).id
        return view_id
