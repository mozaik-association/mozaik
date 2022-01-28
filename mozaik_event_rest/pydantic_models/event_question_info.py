# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List

import pydantic

from odoo.addons.pydantic import models, utils


class EventQuestionAnswerInfo(models.BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class EventQuestionInfo(models.BaseModel):
    id: int
    title: str
    question_type: str
    once_per_order: bool = None
    is_mandatory: bool = None
    answers: List[EventQuestionAnswerInfo] = pydantic.Field([], alias="answer_ids")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
