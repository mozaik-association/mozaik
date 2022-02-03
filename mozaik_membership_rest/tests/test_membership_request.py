# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.http import request

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.base_rest.tests.common import BaseRestCase
from odoo.addons.component.core import WorkContext
from odoo.addons.extendable.tests.common import ExtendableMixin


class MembershipRequestCase(BaseRestCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        collection = _PseudoCollection("membership.rest.services", cls.env)
        cls.services_env = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=request,
        )
        cls.service = cls.services_env.component(usage="membership_request")
        cls.setUpExtendable()

    # pylint: disable=W8106
    def setUp(self):
        # resolve an inheritance issue (common.TransactionCase does not call
        # super)
        BaseRestCase.setUp(self)
        ExtendableMixin.setUp(self)

    def test_post_membership_request(self):
        vals = {
            "lastname": "John",
            "firstname": "Romero",
            "gender": "male",
            "street_man": "Boulevard Herbatte",
            "zip_man": "5000",
            "city_man": "Namur",
            "request_type": "m",
            "auto_validate": False,
        }
        # Create first membership request without autovalidate
        res = self.service.dispatch("post", vals)
        mr = self.env["membership.request"].search(["id", "=", res.id])
        self.assertEqual(mr.id, res.id)
