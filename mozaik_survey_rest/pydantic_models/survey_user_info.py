# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date, datetime
from typing import List

import pydantic

from odoo.addons.pydantic import models, utils

from .survey_question_answer_info import SurveyQuestionAnswerInfo


class SurveyUserInputLineInfo(models.BaseModel):
    id: int
    question_id: int
    answer_type: str = None
    skipped: bool
    value_text_box: str = None
    value_char_box: str = None
    value_numerical_box: float = None
    value_date: date = None
    value_datetime: datetime = None
    suggested_answer_id: SurveyQuestionAnswerInfo = pydantic.Field(
        None, alias="suggested_answer_id"
    )

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class SurveyUserInputInfo(models.BaseModel):
    id: int
    survey_id: int
    user_input_line_ids: List[SurveyUserInputLineInfo] = pydantic.Field(
        None, alias="user_input_line_ids"
    )

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
