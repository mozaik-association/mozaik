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

from .event_question_info import EventQuestionInfo
from .event_stage_info import EventStageInfo
from .event_ticket_info import EventTicketInfo
from .event_type_info import EventTypeInfo
from .event_website_domain_info import EventWebsiteDomainInfo
from .partner_address_info import PartnerAddressInfo
from .partner_minimum_info import PartnerMinimumInfo


class EventShortInfo(BaseModel, metaclass=ExtendableModelMeta):

    id: int
    name: str
    date_begin: datetime
    date_end: datetime
    event_type: EventTypeInfo = pydantic.Field(None, alias="event_type_id")
    stage: EventStageInfo = pydantic.Field(None, alias="stage_id")
    note: str = None
    write_date: datetime
    image_url: str
    interests: List[ThesaurusTermInfo] = pydantic.Field([], alias="interest_ids")
    address: PartnerAddressInfo = pydantic.Field(None, alias="address_id")
    website_domains: List[EventWebsiteDomainInfo] = pydantic.Field(
        [], alias="website_domain_ids"
    )
    website_url: str = None
    description: str = None
    summary: str = None
    visible_on_website: bool = None
    not_indexed_on_website: bool = None
    is_published: bool = None
    is_headline: bool = None

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class EventInfo(EventShortInfo):

    event_tickets: List[EventTicketInfo] = pydantic.Field([], alias="event_ticket_ids")
    seats_limited: bool
    seats_max: int = None
    seats_expected: int = None
    publish_date: date = None
    questions: List[EventQuestionInfo] = pydantic.Field([], alias="question_ids")
    menu_register_cta: bool = None
    organizer: PartnerMinimumInfo = pydantic.Field(None, alias="organizer_id")
