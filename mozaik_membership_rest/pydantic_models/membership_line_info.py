# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date, datetime

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils

from .membership_state_info import MembershipStateInfo
from .subscription_info import SubscriptionInfo


class MembershipLineInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    state: MembershipStateInfo = pydantic.Field(..., alias="state_id")
    subscription: SubscriptionInfo = pydantic.Field(None, alias="product_id")
    price: float = None
    int_instance_id: int
    date_from: date
    date_to: date = None
    active: bool = None
    reference: str = None
    paid: bool = None
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
