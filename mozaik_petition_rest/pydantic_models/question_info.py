# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from typing import List
from odoo.addons.pydantic import models, utils
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
import pydantic
from .answer_info import AnswerInfo

class QuestionInfo(models.BaseModel):
    id: int
    title: str
    question_type: str
    is_mandatory: bool
    answer_ids: List[AnswerInfo] = pydantic.Field([],
                                                        alias="answer_ids")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
