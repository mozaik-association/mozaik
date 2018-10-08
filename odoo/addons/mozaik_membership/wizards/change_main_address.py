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
        domain=lambda s: s._domain_old_int_instance_id(),
        default=lambda s: s._default_old_int_instance_id())
    new_int_instance_id = fields.Many2one(
        'int.instance', string='New Internal Instance',
        compute='_compute_new_int_instance_id',
        store=True)

    @api.model
    def _domain_old_int_instance_id(self):
        """
        Domain of old instance depending of instances of the unique partner
        """
        ids = self.env.context.get('active_ids') or \
            self.env.context.get('active_id') and \
            [self.env.context.get('active_id')] or []

        instance_ids = []
        if len(ids) == 1:
            active_model = self.env.context.get("active_model")
            partner = self.env['res.partner'].browse()
            if active_model == 'postal.coordinate':
                target = self.env['postal.coordinate'].browse(ids)
                partner = target.mapped("partner_id")
            elif active_model == 'res.partner':
                partner = self.env['res.partner'].browse(ids)
            instance_ids = partner.int_instance_ids.ids

        return [('id', 'in', instance_ids)]

    @api.model
    def _default_old_int_instance_id(self):
        """
        If only one instance, take it
        """
        instance_ids = self._domain_old_int_instance_id()[0][2]
        res = False
        if len(instance_ids) == 1:
            res = self.env['int.instance'].browse(instance_ids)
        return res

    @api.model
    def default_get(self, fields_list):
        """
        To get default values for the object.
        """
        res = super().default_get(fields_list)

        ids = self.env.context.get('active_ids') or \
            self.env.context.get('active_id') and \
            [self.env.context.get('active_id')] or []
        res['keeping_mode'] = 1
        res['keep_instance'] = False

        if len(ids) == 1:
            active_model = self.env.context.get("active_model")
            target_model = self._get_target_model()
            if active_model == target_model:
                target = self.env[target_model].browse(ids)
                partner = target.mapped("partner_id")
            else:
                partner = self.env['res.partner'].browse(ids)
            if partner.int_instance_ids:
                res['keep_instance'] = partner.is_company
            res['keeping_mode'] = 3

        return res

    @api.multi
    @api.depends("address_id")
    def _compute_new_int_instance_id(self):
        for wz in self:
            new_int_instance_id = False
            if wz.address_id:
                adr = wz.address_id
                if adr.city_id:
                    new_int_instance_id = \
                        adr.city_id.int_instance_id
            if not new_int_instance_id:
                new_int_instance_id = self.env['int.instance'].\
                    _get_default_int_instance()
            wz.new_int_instance_id = new_int_instance_id

    @api.onchange("address_id", "old_int_instance_id", "new_int_instance_id")
    def _onchange_address_id(self):
        self.ensure_one()
        keeping_mode = 3
        if not self.old_int_instance_id:
            keeping_mode = 1
        elif self.address_id:
            if self.old_int_instance_id != self.new_int_instance_id:
                keeping_mode = 2
        self.keeping_mode = keeping_mode

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
        self_ctx = self
        if self.keeping_mode == 2 and self.keep_instance:
            self_ctx = self.with_context(keep_current_instance=True)

        return super(ChangeMainAddress,
                     self_ctx).button_change_main_coordinate()
