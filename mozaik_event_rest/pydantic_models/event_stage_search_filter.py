# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.event_rest_api.pydantic_models.event_stage_search_filter import (
    EventStageSearchFilter as BaseEventStageSearchFilter,
)


class EventStageSearchFilter(
    BaseEventStageSearchFilter, extends=BaseEventStageSearchFilter
):

    draft_stage: bool = None
