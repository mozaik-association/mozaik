# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from typing import List

import pydantic

from odoo.addons.event_rest_api.pydantic_models.event_info import (
    EventInfo as BaseEventInfo,
)
from odoo.addons.mozaik_thesaurus_api.pydantic_models.thesaurus_term_info import (
    ThesaurusTermInfo,
)

from .event_website_domain_info import EventWebsiteDomainInfo
from .partner_address_info import PartnerAddressInfo


class EventInfo(BaseEventInfo, extends=BaseEventInfo):
    is_private: bool
    interests: List[ThesaurusTermInfo] = pydantic.Field([], alias="interest_ids")
    int_instance_id: int = None
    publish_date: date = None
    website_url: str = None
    address: PartnerAddressInfo = pydantic.Field(None, alias="address_id")
    website_domains: List[EventWebsiteDomainInfo] = pydantic.Field(
        [], alias="website_domain_ids"
    )
