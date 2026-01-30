# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import pydantic

from odoo.addons.mozaik_membership_rest.pydantic_models.membership_request_info import (
    MembershipRequestInfo as BaseMembershipRequestInfo,
)

from .membership_request_origin_info import MembershipRequestOriginInfo


class MembershipRequestInfo(
    BaseMembershipRequestInfo, extends=BaseMembershipRequestInfo
):
    origin: MembershipRequestOriginInfo = pydantic.Field(None, alias="origin_id")
