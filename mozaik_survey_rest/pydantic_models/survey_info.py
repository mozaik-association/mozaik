# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from typing import List

import pydantic

from odoo.addons.mozaik_thesaurus_api.pydantic_models.thesaurus_term_info import (
    ThesaurusTermInfo,
)
from odoo.addons.pydantic import models, utils

from .survey_page_info import SurveyPageInfo
from .survey_question_info import SurveyQuestionInfo


class SurveyShortInfo(models.BaseModel):
    id: int
    title: str
    description: str = None
    interests: List[ThesaurusTermInfo] = pydantic.Field(None, alias="interest_ids")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class SurveyInfo(SurveyShortInfo):
    users_login_required: bool
    page_ids: List[SurveyPageInfo] = pydantic.Field(None, alias="page_ids")
    question_ids: List[SurveyQuestionInfo] = pydantic.Field(None, alias="question_ids")
    questions_layout: str = None
    publish_date: date = None
    is_private: bool
    int_instance_id: int = None
