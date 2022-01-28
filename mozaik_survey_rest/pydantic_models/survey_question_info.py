# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date, datetime
from typing import List

import pydantic

from odoo.addons.pydantic import models, utils

from .survey_question_answer_info import SurveyQuestionAnswerInfo


class SurveyQuestionInfo(models.BaseModel):
    id: int
    title: str
    page_id: int = None
    question_type: str
    description: str = None
    validation_required: bool = False
    validation_email: bool = False
    validation_length_min: int = 0
    validation_length_max: int = 0
    validation_min_float_value: float = 0
    validation_max_float_value: float = 0
    validation_min_date: date = None
    validation_max_date: date = None
    validation_min_datetime: datetime = None
    validation_max_datetime: datetime = None
    validation_error_msg: str = "The answer you entered is not valid."
    constr_mandatory: bool = False
    is_conditional: bool = False
    triggering_question_id: int = None
    matrix_rows: List[SurveyQuestionAnswerInfo] = pydantic.Field(
        None, alias="matrix_row_ids"
    )
    suggested_answers: List[SurveyQuestionAnswerInfo] = pydantic.Field(
        None, alias="suggested_answer_ids"
    )
    matrix_subtype: str = None

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
