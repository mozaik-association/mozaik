# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from typing import List

import pydantic

from odoo.addons.pydantic import models, utils

from .interest_info import InterestInfo
from .milestone_info import MilestoneInfo


class PetitionInfoList(models.BaseModel):
    id: int
    title: str
    description: str = None
    date_begin: date = None
    date_end: date = None
    interest_ids: List[InterestInfo] = pydantic.Field([], alias="interest_ids")
    note: str = None
    milestone_ids: List[MilestoneInfo] = pydantic.Field([], alias="milestone_ids")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
