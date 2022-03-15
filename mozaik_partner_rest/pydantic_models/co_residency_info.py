# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from typing import List

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils

from .address_info import AddressInfo


class CoResidencyInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    address: AddressInfo = pydantic.Field(None, alias="address_id")
    partner_ids: List[int] = []
    line: str = None
    line2: str = None
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
