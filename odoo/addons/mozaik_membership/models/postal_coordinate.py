# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PostalCoordinate(models.Model):

    _inherit = ['postal.coordinate']

    @api.multi
    def _update_partner_int_instance(self):
        """
        Update instance of partner linked to the postal coordinate
        when it becomes main and its `active` field is equal
        to the `active` field of its partner.
        Instance is the default one if no instance found on the city
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
                zip_id = pc.address_id.city_id
                new_int_instance_id = \
                    zip_id.int_instance_id if zip_id \
                    else def_int_instance_id

                if new_int_instance_id != cur_int_instance_id:
                    partner._change_instance(new_int_instance_id)

    @api.model
    def create(self, vals):
        """
        Compute followers and change partner instance if any
        """
        change_instance = not self.env.context.get('keep_current_instance')
        res = super().create(vals)
        if vals.get('is_main') and change_instance:
            res._update_postal_follower()
        return res

    @api.model
    def write(self, vals):
        '''
        Recompute followers and change partner instance if any
        '''
        res = super().write(vals)
        if vals.get('is_main', False):
            self._update_postal_follower()
        return res

    @api.multi
    def _update_postal_follower(self):
        self._update_partner_int_instance()
        self._update_followers()
