# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List

import pydantic

from odoo.addons.event_rest_api.pydantic_models.event_registration_request import (
    EventRegistrationRequest as BaseEventRegistrationRequest,
)

from .event_question_answer import EventQuestionAnswer


class EventRegistrationRequest(
    BaseEventRegistrationRequest, extends=BaseEventRegistrationRequest
):

    zip: str = None
    answers: List[EventQuestionAnswer] = pydantic.Field([])
