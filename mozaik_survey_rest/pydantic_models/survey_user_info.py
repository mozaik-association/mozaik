# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date, datetime
from typing import List

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils

from .survey_question_answer_info import SurveyQuestionAnswerInfo


class SurveyUserInputLineInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    question_id: int
    answer_type: str = None
    skipped: bool = None
    value_text_box: str = None
    value_char_box: str = None
    value_numerical_box: float = None
    value_date: date = None
    value_datetime: datetime = None
    suggested_answer: SurveyQuestionAnswerInfo = pydantic.Field(
        None, alias="suggested_answer_id"
    )
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class SurveyUserInputInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    survey_id: int
    user_input_lines: List[SurveyUserInputLineInfo] = pydantic.Field(
        [], alias="user_input_line_ids"
    )
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
