# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils


class PetitionQuestionAnswerInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    name: str

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class PetitionQuestionInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    title: str
    question_type: str
    is_mandatory: bool = None
    answers: List[PetitionQuestionAnswerInfo] = pydantic.Field([], alias="answer_ids")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
