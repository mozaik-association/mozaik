# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.mozaik_coordinate.tests.common_coordinate_wizard import \
    CommonCoordinateWizard
from odoo.tests.common import TransactionCase


class TestPhoneCoordinateWizard(CommonCoordinateWizard, TransactionCase):

    def setUp(self):
        super(TestPhoneCoordinateWizard, self).setUp()
        self.model_coordinate_wizard = self.env['change.main.phone']
        self.model_coordinate = self.env['phone.coordinate']
        model_phone = self.env['phone.phone']
        self.coo_into_partner = 'mobile_coordinate_id'
        self.coordinate1 = self.env.ref("mozaik_phone.phone_coordinate4")
        self.coordinate2 = self.env.ref("mozaik_phone.phone_coordinate6")
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
