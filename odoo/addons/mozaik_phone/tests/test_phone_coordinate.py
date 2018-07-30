# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase
from odoo.addons.mozaik_coordinate.tests.common_abstract_coordinate import \
    CommonAbstractCoordinate


class TestPhoneCoordinate(CommonAbstractCoordinate, TransactionCase):

    def setUp(self):
        super(TestPhoneCoordinate, self).setUp()
        model_phone = self.env['phone.phone']
        self.model_coordinate = self.env['phone.coordinate']
        # self.field_id_1 = self.env.ref("mozaik_phone.phone_phone_mobile1").id
        # self.field_id_2 = self.env.ref("mozaik_phone.phone_phone_mobile2").id
        self.field_id_1 = model_phone.create({
            'name': '+32 478 85 25 26',
            'type': 'mobile',
        }).id
        self.field_id_2 = model_phone.create({
            'name': '+32 465 00 00 06',
            'type': 'mobile',
        }).id
        self.field_id_3 = model_phone.create({
            'name': '+32 465 00 00 01',
            'type': 'mobile',
        }).id
        self.coo_into_partner = 'mobile_coordinate_id'
