# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from typing import List

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.mozaik_thesaurus_api.pydantic_models.thesaurus_term_info import (
    ThesaurusTermInfo,
)
from odoo.addons.pydantic import utils

from .survey_page_info import SurveyPageInfo
from .survey_question_info import SurveyQuestionInfo


class SurveyShortInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    title: str
    description: str = None
    interests: List[ThesaurusTermInfo] = pydantic.Field([], alias="interest_ids")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class SurveyInfo(SurveyShortInfo):
    users_login_required: bool = None
    pages: List[SurveyPageInfo] = pydantic.Field([], alias="page_ids")
    questions: List[SurveyQuestionInfo] = pydantic.Field([], alias="question_ids")
    questions_layout: str
    publish_date: date = None
    is_private: bool = None
    int_instance_id: int = None
