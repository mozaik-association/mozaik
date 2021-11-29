# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List

from odoo.addons.event_rest_api.pydantic_models.event_search_filter import (
    EventSearchFilter as BaseEventSearchFilter,
)


class EventSearchFilter(BaseEventSearchFilter, extends=BaseEventSearchFilter):

    is_private: bool = None
    website_domain_ids: List[int] = None
    interest_ids: List[int] = None
