# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResUsers(models.Model):

    _inherit = 'res.users'

    def __init__(self, pool, cr):
        """
        Add read access rights on int_instance_m2m_ids
        """
        init_res = super().__init__(pool, cr)
        type(self).SELF_READABLE_FIELDS = self.SELF_READABLE_FIELDS + ['int_instance_m2m_ids']
        return init_res

    def _internal_instances(self, power_level_id=False):
        """
        Cache the int_instance_m2m_ids domain result
        """
        self.ensure_one()
        self_sudo = self.sudo().with_context(active_test=False)
        if not self_sudo.int_instance_m2m_ids:
            return self.env['int.instance'].browse().ids
        dom = [(
            'id', 'child_of', self_sudo.int_instance_m2m_ids.ids
        )]
        if power_level_id:
            dom.append((
                'power_level_id', '=', power_level_id
            ))
        instances = self_sudo.env['int.instance'].search(dom)
        return instances.ids
