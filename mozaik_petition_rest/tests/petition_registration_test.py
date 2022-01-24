# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.http import request
from datetime import date
from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.base_rest.tests.common import BaseRestCase
from odoo.addons.component.core import WorkContext
from odoo.addons.pydantic.tests.common import PydanticMixin


class PetitionRegistration(BaseRestCase, PydanticMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        collection = _PseudoCollection("base.petition.rest.service", cls.env)
        cls.services_env = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=request,
        )
        cls.service = cls.services_env.component(usage="petition.question")

        cls.mand_tick_1 = cls.env["petition.question"].create(
            {
                "title": "Mandatory tickbox 1",
                "question_type": "tickbox",
                "is_mandatory": True,
            }
        )
        cls.mand_tick_2 = cls.env["petition.question"].create(
            {
                "title": "Mandatory tickbox 2",
                "question_type": "tickbox",
                "is_mandatory": True,
            }
        )
        cls.not_mand_tick = cls.env["petition.question"].create(
            {
                "title": "Not mandatory tickbox",
                "question_type": "tickbox",
                "is_mandatory": False,
            }
        )
        cls.open_qu = cls.env["petition.question"].create(
            {
                "title": "Open question",
                "question_type": "text_box",
            }
        )

        question_ids = [
            (4, cls.mand_tick_1.id),
            (4, cls.mand_tick_2.id),
            (4, cls.not_mand_tick.id),
            (4, cls.open_qu.id),
        ]

        cls.petition = (cls.env["petition.petition"]).create(
            {
                "title": "Test Petition",
                "date_begin": date(2021, 10, 13),
                "date_end": date(2021, 10, 16),
                "question_ids": question_ids,
            }
        )
        cls.setUpPydantic()

    # pylint: disable=W8106
    def setUp(self):
        # resolve an inheritance issue (common.TransactionCase does not call
        # super)
        BaseRestCase.setUp(self)
        PydanticMixin.setUp(self)

    def register_answer(self):
        res = self.service.dispatch("get", self.event.id)
        self.assertEqual(res["name"], "Test Event")
