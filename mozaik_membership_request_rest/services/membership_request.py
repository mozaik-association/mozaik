# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.membership_request import (
    MembershipRequest,
    MembershipRequestInfo,
)

@restapi.method(
    routes=[(["/<int:_id>/membership_request"], "POST")],
    input_param=PydanticModelList(MembershipRequest),
    output_param=PydanticModel(MembershipRequestInfo),
    auth="public_or_default",
)
def membership_request(
    membership_request: MembershipRequest
) -> List[MembershipRequestInfo]:
    _logger.debug('Cool des logs')
    return res
