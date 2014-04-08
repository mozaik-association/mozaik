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

import openerp.tests.common as common
from openerp.addons.ficep_coordinate.tests.test_abstract_coordinate import abstract_coordinate


class test_phone_coordinate(abstract_coordinate, common.TransactionCase):

    def setUp(self):
        super(test_phone_coordinate, self).setUp()

        model_phone = self.registry('phone.phone')

        # instanciated members of abstract test
        self.model_coordinate = self.registry('phone.coordinate')
        self.field_id_1 = model_phone.create(self.cr, self.uid, {'name': '+32 478 85 25 25',
                                                                 'type': 'mobile'
                                                                }, context={})
        self.field_id_2 = model_phone.create(self.cr, self.uid, {'name': '+32 465 00 00 00',
                                                                 'type': 'mobile'
                                                                }, context={})
        self.coo_into_partner = 'mobile_coordinate_id'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
