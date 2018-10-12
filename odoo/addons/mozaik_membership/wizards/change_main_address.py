# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class ChangeMainAddress(models.TransientModel):

    _inherit = 'change.main.address'

    keep_instance = fields.Boolean(
        string='Keep Previous Internal Instance?',
    )
    partner_change_instance_ids = fields.One2many(
        comodel_name="partner.change.instance",
        inverse_name="change_main_address_id",
        string="Update instances",
    )

    @api.model
    def default_get(self, fields_list):
        """
        To get default values for the object.
        """
        res = super().default_get(fields_list)
        context = self.env.context
        active_ids = context.get('active_ids', [])
        if not active_ids and context.get('active_id'):
            active_ids = [context.get('active_id')]
        res.update({
            'keep_instance': False,
        })

        active_model = context.get("active_model")
        partners = self.env['res.partner'].browse()
        if active_model == 'postal.coordinate':
            post_coord = self.env['postal.coordinate'].browse(active_ids)
            partners = post_coord.mapped("partner_id")
        elif active_model == 'res.partner':
            partners = self.env['res.partner'].browse(active_ids)
        if len(partners) == 1:
            if partners.int_instance_ids:
                res.update({
                    'keep_instance': partners.is_company,
                })
        items = self.partner_change_instance_ids._build_from_partner(
            partners)
        if items:
            partner_change_instance_ids = [(0, False, i) for i in items]
            res.update({
                'partner_change_instance_ids': partner_change_instance_ids,
            })
        return res

    @api.onchange("address_id")
    def _onchange_address_id(self):
        """
        Onchange used to update the new instance based on the address
        :return:
        """
        self.ensure_one()
        # If we don't have instance on the new address,
        # we can't update anything
        if not self.address_id.city_id.int_instance_id:
            return
        # Do not update when the instance has been forced
        lines = self.partner_change_instance_ids.filtered(
            lambda l: l.origin == 'membership')
        for line in lines:
            instance_address = line.partner_id.city_id.int_instance_id
            if instance_address == line.actual_instance_id:
                # Replace the old instance by the new one
                line.update({
                    'close_subscription': False,
                    'new_instance_id': self.address_id.city_id.int_instance_id,
                })
        # Now, when new_instance_id are filled, we have to check if into these
        # instances, some are equals or useless.
        lines = self.partner_change_instance_ids
        while lines:
            line = fields.first(lines)
            lines -= line
            # If no more lines, useless to do the filtered just after,
            # break directly
            if not lines:
                break
            new_instance = line.new_instance_id
            partner = line.partner_id
            lines_same_instance = lines.filtered(
                lambda l: l.new_instance_id == new_instance and
                l.partner_id == partner)
            if lines_same_instance:
                lines -= lines_same_instance
                # Group lines with the same instance
                lines_same_instance |= line
                # Take the line where actual_instance = new_instance
                # (if not found, use the current line)
                original_line = fields.first(lines_same_instance.filtered(
                    lambda l: l.actual_instance_id == new_instance)) or line
                # Disable the closure
                # Force the new instance
                original_line.update({
                    'close_subscription': False,
                    'new_instance_id': new_instance,
                })
                # For the others, we have to close them
                # We can't not remove the new_instance_id in case of the user
                # change many time the address_id. We have to keep the
                # possibility to execute the onchange many times
                # (not possible if we remove the new_instance_id)
                (lines_same_instance - original_line).update({
                    'close_subscription': True,
                })

    @api.multi
    def button_change_main_coordinate(self):
        """
        Change main coordinate for a list of partners
        * a new main coordinate is created for each partner
        * the previsous main coordinate is invalidated or not regarding
          the option ``invalidate_previous_coordinate``
        :raise: ERROR if no partner selected
        """
        self.ensure_one()
        result = super().button_change_main_coordinate()
        if not self.keep_instance:
            self.partner_change_instance_ids._execute_update()
        return result
