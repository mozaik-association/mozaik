# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class ChangeMainAddress(models.TransientModel):

    _inherit = 'change.main.address'

    keeping_mode = fields.Integer(string='Mode')
    # 1: mandatory
    # 2: user's choice
    # 3: forbiden
    keep_instance = fields.Boolean(
        string='Keep Previous Internal Instance?')
    old_int_instance_id = fields.Many2one(
        'int.instance', string='Previous Internal Instance',
        ondelete='cascade')
    new_int_instance_id = fields.Many2one(
        'int.instance', string='New Internal Instance',
        ondelete='cascade')

    @api.model
    def default_get(self, fields_list):
        """
        To get default values for the object.
        """
        res = super().default_get(fields_list)

        ids = self.env.context.get('active_ids') or \
            self.env.context.get('active_id') and \
            [self.env.context.get('active_id')] or []
        active_model = self.env.context.get("active_model")
        res['keeping_mode'] = 1
        res['keep_instance'] = False

        if len(ids) == 1:
            target_model = self._get_target_model()
            if active_model == target_model:
                target = self.env[target_model].browse(ids)
                partners = target.mapped("partner_id")
            else:
                partners = self.env['res.partner'].browse(ids)
            for partner in partners:
                if partner.int_instance_id:
                    res['keep_instance'] = partner.is_company
                    res['old_int_instance_id'] = partner.int_instance_id.id
            res['keeping_mode'] = 3

        return res

    @api.onchange("address_id")
    def _onchange_address_id(self):
        self.ensure_one()
        new_int_instance_id = False
        keeping_mode = 3
        if not self.old_int_instance_id:
            keeping_mode = 1
        elif self.address_id:
            adr = self.address_id
            if adr.city_id:
                new_int_instance_id = \
                    adr.city_id.int_instance_id.id
            else:
                new_int_instance_id = self.env['int.instance']. \
                    _get_default_int_instance()
            if self.old_int_instance_id != new_int_instance_id:
                keeping_mode = 2
        self.new_int_instance_id = new_int_instance_id
        self.keeping_mode = keeping_mode

    @api.multi
    def button_change_main_coordinate(self):
        """
        Change main coordinate for a list of partners
        * a new main coordinate is created for each partner
        * the previsous main coordinate is invalidates or not regarding
          the option ``invalidate_previous_coordinate``
        :raise: ERROR if no partner selected
        """
        self.ensure_one()
        self_ctx = self
        if self.keeping_mode == 2 and self.keep_instance:
            self_ctx = self.with_context(keep_current_instance=True)

        return super(ChangeMainAddress,
                     self_ctx).button_change_main_coordinate()
