# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.addons.event_rest_api.pydantic_models.event_stage_info import (
    EventStageInfo as BaseEventStageInfo,
)


class EventStageInfo(BaseEventStageInfo, extends=BaseEventStageInfo):
    draft_stage: bool
