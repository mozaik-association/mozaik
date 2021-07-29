# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):

    def test_unauthorized(self):
        """
        Check for compute method of unauthorized partner's flag
        """
        # get a partner and one of its coordinates
        nicolas = self.browse_ref('mozaik_coordinate.res_partner_nicolas')
        coord = self.browse_ref('mozaik_email.email_coordinate_nicolas')
        # Nicolas has no unauthorized coordinates
        self.assertFalse(nicolas.unauthorized)
        # mark the coordinate as unauthorized
        coord.unauthorized = True
        # Nicolas is then unauthorized
        self.assertTrue(nicolas.unauthorized)
        # invalidate the coordinate
        coord.action_invalidate()
        # Nicolas isn't unauthorized any longer
        self.assertFalse(nicolas.unauthorized)
        return
