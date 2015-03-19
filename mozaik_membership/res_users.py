# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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

    def internal_instances(self, cr, uid, power_level_id=False):
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

    def internal_assemblies(self, cr, uid, power_level_id=False):
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

    def internal_mandates(self, cr, uid):
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
