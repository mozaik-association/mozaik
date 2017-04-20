# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_person, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_person is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_person is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_person.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


class partner_involvement_category(orm.Model):

    _name = 'partner.involvement.category'
    _inherit = ['mozaik.abstract.model']
    _description = 'Partner Involvement Category'

    _columns = {
        'name': fields.char('Involvement Category',
                            required=True, select=True,
                            track_visibility='onchange'),
        'note': fields.text('Notes', track_visibility='onchange'),
        'res_users_ids': fields.many2many(
            'res.users', 'involvement_category_res_users_rel',
            id1='category_id', id2='user_id',
            string='Owners', required=True),
    }

    _defaults = {
        'res_users_ids': lambda self, cr, uid, c: [uid],
    }

# constraints

    _unicity_keys = 'name'

# orm methods

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Mark the name as (copy)
        """
        default = default or {}
        res = super(partner_involvement_category, self).copy_data(
            cr, uid, ids, default=default, context=context)
        res.update({
            'name': _('%s (copy)') % res.get('name'),
        })
        owners = [uid]
        if 'res_users_ids' in res:
            try:
                owners = res['res_users_ids'][0][2]
            except:
                pass
            if uid not in owners:
                owners = [uid]
        res['res_users_ids'] = [(6, 0, owners)]
        return res


class partner_involvement(orm.Model):

    _name = 'partner.involvement'
    _inherit = ['mozaik.abstract.model']
    _description = 'Partner Involvement'

    _columns = {
        'partner_id': fields.many2one(
            'res.partner', string='Partner',
            required=True, select=True, track_visibility='onchange'),
        'partner_involvement_category_id': fields.many2one(
            'partner.involvement.category', string='Involvement Category',
            required=True, select=True, track_visibility='onchange'),
        'note': fields.text('Notes', track_visibility='onchange'),
    }

    _rec_name = 'partner_involvement_category_id'

# constraints

    _unicity_keys = 'partner_id, partner_involvement_category_id'

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        """
        :rtype: list of tuples [(,)]
        :rparam: the name of the involvement category for each involvement
        """
        if context is None:
            context = {}
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            if record.partner_involvement_category_id:
                res.append(
                    (record.id, record.partner_involvement_category_id.name)
                )
        return res

    def copy(self, cr, uid, ids, default=None, context=None):
        flds = self.read(cr, uid, ids, ['active'], context=context)
        if flds.get('active', True):
            raise orm.except_orm(
                _('Error'),
                _('An active involvement cannot be duplicated!'))
        res = super(partner_involvement, self).copy(
            cr, uid, ids, default=default, context=context)
        return res
