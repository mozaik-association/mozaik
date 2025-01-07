# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.addons.mozaik_membership_rest.pydantic_models.membership_request import (
    MembershipRequest as BaseMembershipRequest,
)


class MembershipRequest(BaseMembershipRequest, extends=BaseMembershipRequest):
    sponsor_id: int = None
