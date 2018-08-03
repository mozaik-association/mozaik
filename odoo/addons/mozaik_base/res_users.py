# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_base, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_base is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_base is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_base.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp import tools
from openerp.tools import SUPERUSER_ID


class res_users(orm.Model):

    _inherit = 'res.users'

    def _create_welcome_message(self, cr, uid, user, context=None):
        '''
        Do not send welcome message
        '''
        return False

    _defaults = {
        'groups_id': False,
        'display_groups_suggestions': False,
    }

    _order = 'partner_id'

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        '''
        Add the users's login in the record name
        '''
        uid = SUPERUSER_ID
        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []
        records = self.read(cr, uid, ids, ['name', 'login'], context=context)
        for record in records:
            name = '%s (%s)' % (record['name'], record['login'])
            res.append((record['id'], name))
        return res

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Apply also copy_data() for related partner
        (maybe it's a bug, it should be native)
        """
        default = default or {}
        p_id = self.read(
            cr, uid, ids, ['partner_id'], context=context)['partner_id'][0]
        default = self.pool['res.partner'].copy_data(
            cr, uid, p_id, default=default, context=context)
        res = super(res_users, self).copy_data(
            cr, uid, ids, default=default, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        '''
        Invalidate cache when updating user
        '''
        # this write() will clear the cache of the _context_get() here under
        res = super(res_users, self).write(cr, uid, ids, vals, context=context)
        # while this explicit clear_cache() will clear the cache of the native
        # _context_get() in .../odoo/openerp/addons/base/res/res_users.py
        super(res_users, self)._context_get.clear_cache(self)
        return res

    def _apply_ir_rules(self, cr, uid, query, mode='read', context=None):
        '''
        Grant a 100% visibility on users to everybody
        '''
        context = context or {}
        if mode != 'read' or context.get('force_apply_rules') or \
                context.get('apply_for_read', 'read') != 'read':
            super(res_users, self)._apply_ir_rules(
                cr, uid, query, mode=mode, context=context)
        pass

# override public methods

    @tools.ormcache(skiparg=2)
    def _context_get(self, cr, uid, context=None):
        '''
        Add in the users's context:
        - a flag related to each Mozaik group
        - the date format associated to the user's lang
        '''
        result = super(res_users, self)._context_get(cr, uid)
        user = self.browse(cr, SUPERUSER_ID, uid, context)
        imd_obj = self.pool['ir.model.data']
        _, appl_id = imd_obj.get_object_reference(
            cr, uid, 'base', 'module_category_political_association')
        dev_id = imd_obj.xmlid_to_res_id(
            cr, uid, 'mozaik_base.res_groups_developper')
        for g in user.groups_id:
            if g.category_id.id == appl_id:
                result.update({'in_%s' % g.name.lower().replace(' ', '_'): 1})
            elif g.id == dev_id:
                result.update({'is_developper': 1})
        result.update({
            'date_format': self.pool['res.lang']._get_date_format(
                cr, uid, result)
        })
        return result
