# Copyright 2021 ACSONE SA/NV
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

from .petition_milestone_info import PetitionMilestoneInfo
from .petition_question_info import PetitionQuestionInfo


class PetitionShortInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    title: str
    date_begin: date
    date_end: date
    interest_ids: List[ThesaurusTermInfo] = pydantic.Field([], alias="interest_ids")
    note: str = None
    milestone_ids: List[PetitionMilestoneInfo] = pydantic.Field(
        [], alias="milestone_ids"
    )

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class PetitionInfo(PetitionShortInfo):
    description: str = None
    is_private: bool = None
    internal_instance_id: int = None
    question_ids: List[PetitionQuestionInfo] = pydantic.Field([], alias="question_ids")
