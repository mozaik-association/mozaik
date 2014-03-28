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


class allow_duplicate_wizard(orm.TransientModel):

    _inherit = "allow.duplicate.wizard"

    _columns = {
        'co_residency_id': fields.many2one('co.residency', string='Co-Residency'),
    }

    def button_allow_duplicate(self, cr, uid, ids, context=None, vals=None):
        """
        ======================
        button_allow_duplicate
        ======================
        Add co_residency_id into vals and call super ``button_allow_duplicate``
        """
        if vals is None:
            vals = {}
        wizards = self.browse(cr, uid, ids, context=context)
        for wizard in wizards:
            if wizard.co_residency_id:
                vals = {'co_residency_id': wizard.co_residency_id.id}
        super(allow_duplicate_wizard, self).button_allow_duplicate(cr, uid, ids, vals=vals, context=context)

    def get_domain_search(self, cr, uid, ids, domain, context=None):
        """
        =================
        get_domain_search
        =================
        Add co_residency_id's wizard to the domain
        """
        wizard = self.browse(cr, uid, ids, context=context)
        return domain + [('co_residency_id', '=', wizard[0].co_residency_id.id)]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
