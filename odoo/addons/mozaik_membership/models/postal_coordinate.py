# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PostalCoordinate(models.Model):

    _inherit = ['postal.coordinate']

    @api.multi
    def _update_partner_int_instance(self):
        """
        Update instance of partner linked to the postal coordinate case where
        coordinate is main and `active` field has same value than
        `partner.active`
        Instance is the default one if no instance for the postal coordinate
        otherwise it is its instance
        """
        for pc in self:
            # if coordinate is main update int_instance of partner
            if pc.is_main and pc.active == pc.partner_id.active and \
                    pc.partner_id.membership_state_id:
                partner = pc.partner_id
                cur_int_instance_id = partner.int_instance_id.id
                def_int_instance_id = self.env['int.instance']\
                    ._get_default_int_instance()
                # get instance_id of address or keep default otherwise
                zip_id = pc.address_id.address_local_zip_id
                new_int_instance_id = \
                    zip_id and zip_id.int_instance_id.id or \
                    def_int_instance_id

                if new_int_instance_id != cur_int_instance_id:
                    partner._change_instance(new_int_instance_id)

    @api.model
    def create(self, vals):
        """
        call `_update_partner_int_instance` if `is_main` is True
        """
        change_instance = not self.env.context.get('keep_current_instance')
        self_ctx = self.with_context(delay_notification=change_instance)
        res = super(PostalCoordinate, self_ctx).create(vals)
        if vals.get('is_main') and change_instance:
            res._update_partner_int_instance()
            res.sudo()._update_followers()
        return res

    @api.model
    def write(self, vals):
        '''
        call `_update_partner_int_instance` if `is_main` is True
        '''
        res = super().write(vals)
        if vals.get('is_main', False):
            self._update_partner_int_instance()
            self.sudo()._update_followers()
        return res
