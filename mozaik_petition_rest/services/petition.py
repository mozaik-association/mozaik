# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.petition_info import PetitionInfo
from ..pydantic_models.petition_info_list import PetitionInfoList


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
        routes=[
            (
                [
                    "/get_list/<int:is_private>/<int:internal_instance_id>/"
                    "<int:visible_on_website>/<string:date_publish>/"
                ],
                "GET",
            ),
            (
                [
                    "/get_list/<int:is_private>/<int:internal_instance_id>/"
                    "<int:visible_on_website>/"
                ],
                "GET",
            ),
        ],
        output_param=PydanticModelList(PetitionInfo),
        auth="public",
    )
    def get_list(
        self,
        is_private: int,
        internal_instance_id: int,
        visible_on_website: int,
        date_publish: str = None,
    ) -> List[PetitionInfoList]:
        domain = []
        if bool(is_private):
            domain.append(("is_private", "=", True))
        if internal_instance_id and internal_instance_id != 0:
            domain.append(("int_instance_id", "=", internal_instance_id))
        if date_publish:
            domain.append(
                ("date_publish", ">=", datetime.strptime(date_publish, "%Y-%m-%d"))
            )
        if bool(visible_on_website):
            domain.append(("visible_on_website", "=", True))
        res: List[PetitionInfoList] = []
        for e in self.env["petition.petition"].sudo().search(domain):
            res.append(PetitionInfoList.from_orm(e))
        return res
