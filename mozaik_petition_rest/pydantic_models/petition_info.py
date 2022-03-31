# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date, datetime
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
from .website_domain_info import WebsiteDomainInfo


class PetitionShortInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    title: str
    date_begin: date
    date_end: date
    signatory_count: int
    image_url: str
    state: str = None
    interest_ids: List[ThesaurusTermInfo] = pydantic.Field([], alias="interest_ids")
    note: str = None
    summary: str = None
    milestone_ids: List[PetitionMilestoneInfo] = pydantic.Field(
        [], alias="milestone_ids"
    )
    visible_on_website: bool = None
    website_domains: List[WebsiteDomainInfo] = pydantic.Field(
        [], alias="website_domain_ids"
    )
    is_headline: bool = None
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class PetitionInfo(PetitionShortInfo):
    description: str = None
    question_ids: List[PetitionQuestionInfo] = pydantic.Field([], alias="question_ids")
