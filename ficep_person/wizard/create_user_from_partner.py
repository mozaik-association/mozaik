# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


#TODO: must be completed with Internal Instances M2M

class create_user_from_partner(orm.TransientModel):

    _name = 'create.user.from.partner'
    _description = 'Wizard to Create a User from a Partner'

    _columns = {
        'portal_only': fields.boolean('Portal only'),
        'nok': fields.char('reason'),
        'login': fields.char('Login', size=64),
        'group_id': fields.many2one('res.groups', string="User's group",
                                    domain="[('category_id','=',appl_id)]"),
        'appl_id': fields.many2one('ir.module.category', string="Application"),
    }

    _defaults = {
        'portal_only': False,
    }

    def default_get(self, cr, uid, fields, context):
        """
        Get default values for the object.
        Compute the reason for which the portal check box is read-only
        :raise: ERROR if no active_id found in the context
        """
        partner_id = context and context.get('active_id', False) or False
        if not partner_id:
            raise orm.except_orm(_('Error'), _('A partner is required to create a new user!'))

        res = super(create_user_from_partner, self).default_get(cr, uid, fields, context=context)

        partner = self.pool['res.partner'].browse(cr, uid, partner_id, context=context)

        nok = False
        if partner.user_ids:
            nok = 'user'
        elif not partner.active:
            nok = 'active'
        elif partner.is_company:
            nok = 'company'
        elif not partner.birth_date:
            nok = 'birthdate'
        elif not partner.email or partner.email.startswith('N/A'):
            nok = 'email'

        res.update({'nok': nok})
        if nok:
            res.update({'portal_only': False})

        return res

    def create_user_from_partner(self, cr, uid, ids, context=None):
        """
        ========================
        create_user_from_partner
        ========================
        Create a user based on the selected partner (active_id) and associate it
        to the choosen group
        :param ids: id of the wizard
        :type ids: int

        **Note**
        This is not a mass wizard. Only one partner can be transformed to a user at a time.
        """
        if context is None:
            context = {}

        partner_id = context.get('active_id')

        wizard = self.browse(cr, uid, ids, context=context)[0]
        if wizard.portal_only:
            _, group_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'portal', 'group_portal')

            partner = self.pool['res.partner'].browse(cr, uid, partner_id, context=context)

            login = partner.email
        else:
            group_id = wizard.group_id.id
            login = wizard.login

        return self.pool['res.partner'].create_user(cr, uid, login, partner_id, [group_id], context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
