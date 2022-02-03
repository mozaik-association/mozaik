# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class PetitionRegistrationAnswer(BaseModel, metaclass=ExtendableModelMeta):
    question_id: int
    value_answer_id: List[int] = None
    value_text_box: str = None
    value_tickbox: bool = None
