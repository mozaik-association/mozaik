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
import base64
import re
import tempfile

import logging
from openerp.osv import orm, fields
from openerp.tools.translate import _

EXPR = re.compile('[/+#]')
_logger = logging.getLogger(__name__)


class streets_repository_loader(orm.TransientModel):

    _name = "streets.repository.loader"
    _description = "Street Repository Loader"

    def _format(self, value):
        """
        :type value: string
        :rparam: value without character `#`,`/` and without
                 space at the beginning or at the end of the string
        """
        return re.sub(EXPR, '', value).strip()

    def _get_streets(self, value, vals):
        """
        ============
        _get_streets
        ============
        :type value: char
        :param value: contains street or street and alternative street
                      separator is `*`
        :type vals: {}
        :post: update vals with
            key:value
            local_street_alternative:alternative_street
            local_street:street
        """
        alternative_street = False
        if '*' in value:
            streets = value.split('*')
            street = streets[0]
            alternative_street = self._format(streets[1])
        else:
            street = value
        street = self._format(street)
        vals['local_street_alternative'] = alternative_street
        vals['local_street'] = street

    _columns = {
        'ref_streets': fields.binary(string='File Referential of Streets'),
    }

    def update_local_streets(self, cr, uid, ids, context=None):
        """
        ====================
        update_local_streets
        ====================
        Read the uploaded file of the wizard and
        create, update or set flag ``to_disable``
        of models ``address.local.street``
        """
        for wiz in self.browse(cr, uid, ids, context=context):
            f = tempfile.NamedTemporaryFile(delete=False)
            f.write(base64.decodestring(wiz.ref_streets))
            f.close()
            with open(f.name) as repository_file:
                for line in repository_file:
                    complete_code = line[:16]  # read code
                    if not complete_code.isdigit() or len(complete_code) != 16:
                        raise orm.except_orm(_('Error'), _('Invalid File Format!'))

                    complete_code = complete_code[8:]  # code to use
                    vals = {'identifier': complete_code[4:],
                            'local_zip': complete_code[:4],
                            'local_street_alternative': False,
                            'local_street': False}
                    domain = [('identifier', '=', vals['identifier']),
                              ('local_zip', '=', vals['local_zip'])]

                    #strip and remove bad character
                    data = self._format(line[16:])

                    local_street_model = self.pool['address.local.street']
                    street_ids = local_street_model.search(cr, uid, domain, context=context)
                    if street_ids:
                        if '-*-' in data:
                            #disable
                            vals = {'to_disable': True}
                            self.pool['address.local.street'].write(cr, uid, street_ids,\
                                                    {'to_disable': True}, context=context)
                        else:
                            #update
                            data = re.split(r'%', line[16:], 1)
                            if data:
                                data = data[0]
                                self._get_streets(data, vals)
                                street_ids = local_street_model.search(cr, uid, domain, context=context)
                                self.pool['address.local.street'].write(cr, uid, street_ids, vals, context=context)
                    else:
                        #create
                        if data != '-*-':
                            try:
                                self._get_streets(data, vals)
                                self.pool['address.local.street'].create(cr, uid, vals, context=context)
                            except:
                                _logger.warning(_('Key for address.local.street already exist'))
                                pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
