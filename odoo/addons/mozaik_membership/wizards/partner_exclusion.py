# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, models, _


class PartnerExclusion(models.TransientModel):
    """
    Wizard used to exclude some partners
    """
    _name = "partner.exclusion"
    _description = "Partner exclusion wizard"

    @api.multi
    def action_exclude(self):
        """
        Action to exclude selected partners
        :return: dict/action
        """
        context = self.env.context
        if context.get('active_model') != 'res.partner':
            raise exceptions.MissingError(
                _("You should use this wizard on partners!"))
        partners = self.env['res.partner'].browse(context.get('active_ids'))
        if partners:
            partners._action_exclude()
        return {}
