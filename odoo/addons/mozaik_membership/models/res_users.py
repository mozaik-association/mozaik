# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class ResUsers(models.Model):

    _inherit = 'res.users'

    int_instance_m2m_ids = fields.Many2many(
        related='partner_id.int_instance_m2m_ids')
    lang = fields.Selection(related='partner_id.lang')

    @api.model
    def _register_hook(self):
        """
        Add read access rights on int_instance_m2m_ids
        """
        init_res = super()._register_hook()
        # duplicate list to avoid modifying the original reference
        self.SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        self.SELF_READABLE_FIELDS.append('int_instance_m2m_ids')
        return init_res

    @api.multi
    def _internal_instances(self, power_level_id=False):
        """
        Cache the int_instance_m2m_ids domain result
        """
        self.ensure_one()
        self_sudo = self.sudo()
        if not self_sudo.int_instance_m2m_ids:
            return self.env['int.instance'].browse()
        dom = [(
            'id', 'child_of', self_sudo.int_instance_m2m_ids.ids
        )]
        if power_level_id:
            dom.append((
                'power_level_id', '=', power_level_id
            ))
        instances = self.env['int.instance'].sudo().search(dom)
        return instances.ids
