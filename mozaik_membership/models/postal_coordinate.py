# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, models, _


class PostalCoordinate(models.Model):

    _inherit = ['postal.coordinate']

    @api.model
    def create(self, vals):
        """
        Compute followers and change partner instance if any
        """
        change_instance = not self.env.context.get('keep_current_instance')
        # If we're into a wizard
        params = self.env.context.get('params')
        if vals.get('is_main') and change_instance and not params:
            address = self.env['address.address'].browse(
                vals.get('address_id'))
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            self._auto_instance_assign(partner, address)
        res = super().create(vals)
        if res.is_main and change_instance:
            res._become_main_coordinate()
        return res

    def write(self, vals):
        '''
        Recompute followers and change partner instance if any
        '''
        if vals.get('is_main'):
            for record in self:
                if vals.get('address_id'):
                    address = self.env['address.address'].browse(
                        vals.get('address_id'))
                else:
                    address = record.address_id
                if vals.get('partner_id'):
                    partner = self.env['res.partner'].browse(
                        vals.get('partner_id'))
                else:
                    partner = record.partner_id
                record._auto_instance_assign(partner, address)
        res = super().write(vals)
        if vals.get('is_main', False):
            self._become_main_coordinate()
        return res

    def _auto_instance_assign(self, partners, address):
        """
        Auto-update the membership line with the new address (if possible).
        If it's not possible, redirect the user to the wizard to do it
        manually.
        :param partners: res.partner recordset
        :param address: address.address recordset
        :return: bool
        """
        # Simulate the wizard to update instance
        wizard_obj = self.env['change.main.address']
        context = self.env.context
        for partner in partners:
            values = {
                'keep_instance': False,
                'address_id': address.id,
            }
            wizard_context = context.copy()
            wizard_context.update({
                'active_model': partner._name,
                'active_ids': partner.ids,
                'active_id': partner.id,
            })
            wizard = wizard_obj.with_context(wizard_context).create(values)
            # Simulate onchange
            try:
                wizard._onchange_address_id()
            except exceptions.ValidationError:
                self._auto_update_instance_impossible(partner)
            # If we have 1 line with close_subscription set to True, it's
            # because we have at least 1 duplicate (about current instance and
            # new instance). So we have to abort the auto-update and propose
            # to the user to use the wizard.
            if wizard.partner_change_instance_ids.filtered(
                    "close_subscription"):
                self._auto_update_instance_impossible(partner)

            wizard._update_instances()
        return True

    @api.model
    def _auto_update_instance_impossible(self, partner):
        """
        Raise the exception when it's not possible to update automatically
        instances on membership lines.
        :param partner: res.partner recordset
        :return:
        """
        msg = _("This partner (%s) has many membership lines. The system can "
                "not update automatically related instances.\n"
                "Please use the wizard to change the main address on the "
                "related partner") % partner.display_name
        raise exceptions.ValidationError(msg)

    def _become_main_coordinate(self):
        """
        Current recordset become main postal coordinate
        :return: bool
        """
        self._update_followers()
        return True
