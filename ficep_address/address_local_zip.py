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


class address_local_zip(orm.Model):

    _name = 'address.local.zip'
    _description = "Address Local Zip"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'local_zip': fields.integer('Local Zip', required=True),
    }

    _rec_name = 'local_zip'

    _sql_constraints = [
        ('check_unicity_zip', 'unique(local_zip)', _('This street already exist for this given zip code!'))
    ]

    _order = "local_zip"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
