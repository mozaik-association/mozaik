# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from typing import List

import pydantic

from odoo.addons.event_rest_api.pydantic_models.event_info import (
    EventInfo as BaseEventInfo,
    EventShortInfo as BaseEventShortInfo,
)
from odoo.addons.mozaik_thesaurus_api.pydantic_models.thesaurus_term_info import (
    ThesaurusTermInfo,
)

from .event_question_info import EventQuestionInfo
from .event_website_domain_info import EventWebsiteDomainInfo
from .partner_address_info import PartnerAddressInfo


class EventShortInfo(BaseEventShortInfo, extends=BaseEventShortInfo):
    interests: List[ThesaurusTermInfo] = pydantic.Field([], alias="interest_ids")
    address: PartnerAddressInfo = pydantic.Field(None, alias="address_id")
    website_domains: List[EventWebsiteDomainInfo] = pydantic.Field(
        [], alias="website_domain_ids"
    )
    website_url: str = None
    description: str = None


class EventInfo(BaseEventInfo, extends=BaseEventInfo):
    publish_date: date = None
    questions: List[EventQuestionInfo] = pydantic.Field([], alias="question_ids")
    menu_register_cta: bool = None
