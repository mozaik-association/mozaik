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

from openerp.osv import orm
from openerp.tools.translate import _
from openerp.tools import SUPERUSER_ID


class allow_duplicate_wizard(orm.TransientModel):

    _name = "allow.duplicate.wizard"

    def button_allow_duplicate(self, cr, uid, ids, vals=None, context=None):
        if vals is None:
            vals = {}
        if context is None:
            context = {}
        if not context.get('active_model', False):
            raise orm.except_orm(_('Error'), _('Missing active_model in context'))

        target_obj = self.pool[context.get('active_model')]
        discriminant_field = target_obj._discriminant_field
        document_ids = context.get('active_ids')

        documents = target_obj.browse(cr, uid, document_ids, context=context)
        discriminants = []
        for document in documents:
            if not document['is_duplicate_detected']:
                raise orm.except_orm(_('Error'), _('Only duplicated entries are allowed!'))
            discriminants.append(document[discriminant_field])

        if len(set(discriminants)) != 1:
            raise orm.except_orm(_('Error'), _('Only duplicated entries related to the same field "%s" are allowed!') % target_obj._columns[discriminant_field].string)

        if len(document_ids) == 1:
            discriminant = target_obj._is_discriminant_m2o() and discriminants[0].id or discriminants[0]
            domain_search = [(discriminant_field, '=', discriminant),
                             ('is_duplicate_allowed', '=', True)]
            domain_search = self.get_domain_search(cr, uid, ids, domain_search, context=context)
            allowed_document_ids = target_obj.search(cr, SUPERUSER_ID, domain_search, context=context)
            if not allowed_document_ids:
                raise orm.except_orm(_('Error'), _('You must select more than one entry!'))
        vals.update(target_obj.get_fields_to_update(cr, uid, "allow", context=context))
        target_obj.write(cr, uid, document_ids, vals, context=context)

    def get_domain_search(self, cr, uid, ids, domain, context=None):
        return domain

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
