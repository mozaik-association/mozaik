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
import tempfile
import logging

from openerp.osv import orm, fields
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class streets_repository_loader(orm.TransientModel):

    _name = "streets.repository.loader"
    _description = "Streets Repository Loader"

    _columns = {
        'ref_streets': fields.binary(string='File to Load', required=True),
    }

    def update_local_streets(self, cr, uid, ids, context=None):
        """
        ====================
        update_local_streets
        ====================
        Read the uploaded file and
        create, update or disable local streets
        """
        _logger.info('Start Streets Loader...')
        local_street_model = self.pool['address.local.street']
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
                    zipcode = complete_code[:4]
                    identifier = complete_code[4:]

                    line = line[16:]
                    line = line.split('#', 1)[0]
                    line = line.split('%', 1)[0]
                    line = line.replace('/', '')
                    disabled = line == '-*-'

                    domain = [('local_zip', '=', zipcode), ('identifier', '=', identifier)]
                    street_ids = local_street_model.search(cr, uid, domain, context=context)

                    if not disabled:
                        alts = line.split('*', 1)

                        with_alt = len(alts) == 2
                        street1 = alts[0].strip()
                        street2 = with_alt and alts[1].strip() or False

                        streets = {
                            'local_street': street1,
                            'local_street_alternative': street2,
                        }

                        if not street_ids:
                            if with_alt:
                                domain = [('local_zip', '=', zipcode), '|', ('local_street', '=', street1), ('local_street_alternative', '=', street2)]
                            else:
                                domain = [('local_zip', '=', zipcode), ('local_street', '=', street1)]
                            street_ids = local_street_model.search(cr, uid, domain, context=context)

                        if street_ids:
                            #update
                            local_street_model.write(cr, uid, street_ids, streets, context=context)
                        else:
                            #create
                            streets.update({
                                'local_zip': zipcode,
                                'identifier': identifier,
                            })
                            local_street_model.create(cr, uid, streets, context=context)
                    elif street_ids:
                        #disable
                        vals = {'disabled': True}
                        local_street_model.write(cr, uid, street_ids, vals, context=context)
                    else:
                        _logger.warning('Unknown identifier to disable %s%s' % (zipcode, identifier))

        _logger.info('Stop Streets Loader')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
