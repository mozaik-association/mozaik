# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.mail_blacklist_info import MailBlacklistInfo


class MailBlacklistService(Component):
    _inherit = "base.mail.rest.service"
    _name = "mail.blacklist.rest.service"
    _usage = "mail_blacklist"
    _expose_model = "mail.blacklist"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(MailBlacklistInfo),
    )
    def get(self, _id: int) -> MailBlacklistInfo:
        mail_blacklist = self._get(_id)
        return MailBlacklistInfo.from_orm(mail_blacklist)

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        output_param=PydanticModelList(MailBlacklistInfo),
    )
    def search(self) -> List[MailBlacklistInfo]:
        res: List[MailBlacklistInfo] = []
        for m in self.env["mail.blacklist"].sudo().search([]):
            res.append(MailBlacklistInfo.from_orm(m))
        return res

    @restapi.method(
        routes=[(["/add/<string:_email>"], "POST")],
        output_param=PydanticModel(MailBlacklistInfo),
    )
    def add(self, _email: str) -> MailBlacklistInfo:
        mail_blacklist = self.env["mail.blacklist"].create({"email": _email})
        return MailBlacklistInfo.from_orm(mail_blacklist)
