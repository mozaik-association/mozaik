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


class partner_involvement(orm.Model):

    _name = 'partner.involvement'
    _inherit = ['abstract.ficep.model']

    _columns = {
        'partner_id': fields.many2one('res.partner', string='Related Partner', required=True, track_visibility='onchange'),
        'partner_involvement_category_id': fields.many2one('partner.involvement.category', required=True, string='Involvement Category', track_visibility='onchange'),
    }

    _rec_name = 'partner_involvement_category_id'

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
                res.append((record.id, record.partner_involvement_category_id.name))
        return res

    def copy(self, cr, uid, ids, default=None, context=None):
        flds = self.read(cr, uid, ids, ['active'], context=context)
        if flds.get('active', True):
            raise orm.except_orm(_('Error'), _('An active involvement cannot be duplicated!'))
        res = super(partner_involvement, self).copy(cr, uid, ids, default=default, context=context)
        return res


class partner_involvement_category(orm.Model):

    _name = 'partner.involvement.category'
    _inherit = ['abstract.ficep.model']

    _columns = {
        'name': fields.char('Involvement Category', required=True, select=True, track_visibility='onchange'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
