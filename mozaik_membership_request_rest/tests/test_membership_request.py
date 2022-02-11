# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.http import request

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.base_rest.tests.common import BaseRestCase
from odoo.addons.component.core import WorkContext
from odoo.addons.pydantic.tests.common import PydanticMixin


class MembershipRequestCase(BaseRestCase, PydanticMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        collection = _PseudoCollection("membership.request.rest.services", cls.env)
        cls.services_env = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=request,
        )
        cls.service = cls.services_env.component(usage="membership_request")

        cls.setUpPydantic()

    def setUp(self):
        # resolve an inheritance issue (common.TransactionCase does not call
        # super)
        BaseRestCase.setUp(self)
        PydanticMixin.setUp(self)

    def test_post_membership_request(self):
        vals = {
            "lastname": "John",
            "firstname": "Romero",
            "gender": "male",
            "street_man": "Boulevard Herbatte",
            "zip_man": "5000",
            "city_man": "Namur",
            "request_type": "m",
        }
        # Create first membership request without autovalidate
        res = self.service.dispatch("membership_request", (0), params=vals)
        mr = self.env["membership.request"].browse(res["id"])
        self.assertEqual(mr.id, res["id"])
        self.assertEqual(mr.state, "draft")

        # Create first membership request with autovalidate
        res = self.service.dispatch("membership_request", (1), params=vals)
        mr = self.env["membership.request"].browse(res["id"])
        self.assertEqual(mr.id, res["id"])
        self.assertEqual(mr.state, "validate")
