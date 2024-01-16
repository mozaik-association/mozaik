# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils

from .involvement_category_info import InvolvementCategoryInfo


class InvolvementInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    partner_id: int
    involvement_category: InvolvementCategoryInfo = pydantic.Field(
        ..., alias="involvement_category_id"
    )
    effective_time: datetime = None
    importance_level: str = None
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
