# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List

from odoo.addons.pydantic import models


class PetitionRegistrationAnswer(models.BaseModel):
    question_id: int
    value_answer_id: List[int] = None
    value_text_box: str = None
    value_tickbox: bool = None
