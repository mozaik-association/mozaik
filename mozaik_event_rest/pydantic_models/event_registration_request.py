# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from .event_question_answer import EventQuestionAnswer


class EventRegistrationRequest(BaseModel, metaclass=ExtendableModelMeta):

    firstname: str = None
    lastname: str = None
    email: str = None
    phone: str = None
    mobile: str = None
    event_ticket_id: int = None
    registered_partner_id: int = None
    zip: str = None
    answers: List[EventQuestionAnswer] = pydantic.Field([])
    force_autoval: bool = False


class EventRegistrationRequestList(BaseModel, metaclass=ExtendableModelMeta):

    event_registration_requests: List[EventRegistrationRequest] = []
