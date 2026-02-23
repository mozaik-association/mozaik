# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


from odoo.addons.mozaik_membership_rest.pydantic_models.membership_request_info import (
    MembershipRequestInfo as BaseMembershipRequestInfo,
)


class MembershipRequestInfo(
    BaseMembershipRequestInfo, extends=BaseMembershipRequestInfo
):
    autovalidation_type: str = None
