# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date, datetime
from typing import List

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils

from .survey_question_answer_info import SurveyQuestionAnswerInfo


class SurveyQuestionInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    title: str
    page_id: int = None
    question_type: str = None
    description: str = None
    validation_required: bool = None
    validation_email: bool = None
    validation_length_min: int = None
    validation_length_max: int = None
    validation_min_float_value: float = None
    validation_max_float_value: float = None
    validation_min_date: date = None
    validation_max_date: date = None
    validation_min_datetime: datetime = None
    validation_max_datetime: datetime = None
    validation_error_msg: str = None
    constr_mandatory: bool = None
    is_conditional: bool = None
    triggering_question_id: int = None
    matrix_rows: List[SurveyQuestionAnswerInfo] = pydantic.Field(
        [], alias="matrix_row_ids"
    )
    suggested_answers: List[SurveyQuestionAnswerInfo] = pydantic.Field(
        [], alias="suggested_answer_ids"
    )
    matrix_subtype: str = None
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
