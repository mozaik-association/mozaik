# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4
from odoo.addons.mozaik_coordinate.tests.common_failure_editor import \
    CommonFailureEditor
from odoo.tests.common import TransactionCase


class TestEmailFailure(CommonFailureEditor, TransactionCase):

    def setUp(self):
        super(TestEmailFailure, self).setUp()
        self.model_coordinate = self.env['email.coordinate']
        self.coo_into_partner = 'email_coordinate_id'
        self.coordinate = self.model_coordinate.create({
            'email': '%s@mozaik-email.test' % str(uuid4()),
            'partner_id': self.partner1.id,
        })
