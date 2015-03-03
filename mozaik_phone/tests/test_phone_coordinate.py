# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_phone, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_phone is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_phone is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_phone.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp.tests.common as common
from openerp.addons.mozaik_coordinate.tests.test_abstract_coordinate import \
    abstract_coordinate


class test_phone_coordinate(abstract_coordinate, common.TransactionCase):

    def setUp(self):
        super(test_phone_coordinate, self).setUp()

        model_phone = self.registry('phone.phone')

        # instanciated members of abstract test
        self.model_coordinate = self.registry('phone.coordinate')
        self.field_id_1 = model_phone.create(
            self.cr, self.uid, {
                'name': '+32 478 85 25 25', 'type': 'mobile'}, context={})
        self.field_id_2 = model_phone.create(
            self.cr, self.uid, {
                'name': '+32 465 00 00 00', 'type': 'mobile'}, context={})
        self.field_id_3 = model_phone.create(
            self.cr, self.uid, {
                'name': '+32 465 00 00 01', 'type': 'mobile'}, context={})
        self.coo_into_partner = 'mobile_coordinate_id'
