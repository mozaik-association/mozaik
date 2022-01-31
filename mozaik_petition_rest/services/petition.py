# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.petition_info import PetitionInfo, PetitionShortInfo
from ..pydantic_models.petition_registration_info import PetitionRegistrationInfo
from ..pydantic_models.petition_registration_request import PetitionRegistrationRequest
from ..pydantic_models.petition_search_filter import PetitionSearchFilter


class PetitionService(Component):
    _inherit = "base.petition.rest.service"
    _name = "petition.rest.service"
    _usage = "petition"
    _expose_model = "petition.petition"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(PetitionInfo),
        auth="public",
    )
    def get(self, _id: int) -> PetitionInfo:
        petition = self._get(_id)
        return PetitionInfo.from_orm(petition)

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(PetitionSearchFilter),
        output_param=PydanticModelList(PetitionShortInfo),
        auth="public",
    )
    def search(
        self, petition_search_filter: PetitionSearchFilter
    ) -> List[PetitionShortInfo]:
        domain = []
        if petition_search_filter.is_private is not None:
            domain.append(("is_private", "=", petition_search_filter.is_private))
        if petition_search_filter.internal_instance_id:
            domain.append(
                ("int_instance_id", "=", petition_search_filter.internal_instance_id)
            )
        if petition_search_filter.date_publish:
            domain.append(
                (
                    "date_publish",
                    ">=",
                    datetime.strptime(petition_search_filter.date_publish, "%Y-%m-%d"),
                )
            )
        if petition_search_filter.visible_on_website is not None:
            domain.append(
                ("visible_on_website", "=", petition_search_filter.visible_on_website)
            )
        res: List[PetitionShortInfo] = []
        for petition in self.env["petition.petition"].sudo().search(domain):
            res.append(PetitionShortInfo.from_orm(petition))
        return res

    @restapi.method(
        routes=[(["/<int:_id>/register_answer"], "POST")],
        input_param=PydanticModel(PetitionRegistrationRequest),
        output_param=PydanticModel(PetitionRegistrationInfo),
        auth="public",
    )
    def register_answer(
        self, _id: int, petition_registration_request: PetitionRegistrationRequest
    ) -> PetitionRegistrationInfo:
        registration_values = {
            "petition_id": self._get(_id).id,
            "firstname": petition_registration_request.firstname,
            "lastname": petition_registration_request.lastname,
            "email": petition_registration_request.email,
            "mobile": petition_registration_request.mobile,
            "zip": petition_registration_request.zip,
            "date_open": petition_registration_request.date_open,
        }
        answers = []
        for answer in petition_registration_request.answers:
            answers.append(
                (
                    0,
                    0,
                    {
                        "question_id": answer.question_id,
                        "value_answer_id": answer.value_answer_id,
                        "value_text_box": answer.value_text_box,
                        "value_tickbox": answer.value_tickbox,
                    },
                )
            )
        registration_values["registration_answer_ids"] = answers
        petition_registration = (
            self.env["petition.registration"]
            .with_context(autoval=True)
            .create(registration_values)
        )
        return PetitionRegistrationInfo.from_orm(petition_registration)
