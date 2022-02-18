# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from typing import List

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils


class EventQuestionAnswerInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    name: str
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class EventQuestionInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    title: str
    question_type: str
    once_per_order: bool = None
    is_mandatory: bool = None
    answers: List[EventQuestionAnswerInfo] = pydantic.Field([], alias="answer_ids")
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter