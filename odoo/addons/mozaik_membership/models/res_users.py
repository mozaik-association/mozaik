# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields
from openerp.osv import orm
from openerp.tools import SUPERUSER_ID


class res_users(orm.Model):

    _inherit = 'res.users'

    int_instance_m2m_ids = fields.Many2many(
        related='partner_id.int_instance_m2m_ids', inherited=True)

    lang = fields.Selection(related='partner_id.lang', inherited=True)

    def _register_hook(self, cr):
        """
        Add read access rights on int_instance_m2m_ids
        """
        init_res = super(res_users, self)._register_hook(cr)
        # duplicate list to avoid modifying the original reference
        self.SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        self.SELF_READABLE_FIELDS.append('int_instance_m2m_ids')
        return init_res

    def _internal_instances(self, cr, uid, power_level_id=False):
        """
        Cache the int_instance_m2m_ids domain result
        """
        user = self.pool['res.users'].browse(cr, SUPERUSER_ID, [uid])[0]
        if not user.partner_id.int_instance_m2m_ids.ids:
            return []
        dom = [(
            'id', 'child_of', user.partner_id.int_instance_m2m_ids.ids
        )]
        if power_level_id:
            dom.append((
                'power_level_id', '=', power_level_id
            ))
        ids = self.pool['int.instance'].search(cr, SUPERUSER_ID, dom)
        return ids

    def _internal_assemblies(self, cr, uid, power_level_id=False):
        """
        Compute internal assembly ids readable by the user
        """
        inst_ids = self.internal_instances(cr, uid, power_level_id)
        if not inst_ids:
            return []
        dom = [(
            'instance_id', 'in', inst_ids
        )]
        ids = self.pool['int.assembly'].search(cr, SUPERUSER_ID, dom)
        return ids

    def _internal_mandates(self, cr, uid):
        """
        Compute internal mandate ids readable by the user
        """
        ass_ids = self.internal_assemblies(cr, uid)
        if not ass_ids:
            return []
        dom = [(
            'int_assembly_id', 'in', ass_ids
        )]
        ids = self.pool['int.mandate'].search(cr, SUPERUSER_ID, dom)
        return ids
