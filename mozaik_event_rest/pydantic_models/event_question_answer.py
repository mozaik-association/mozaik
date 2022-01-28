# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.pydantic import models


class EventQuestionAnswer(models.BaseModel):

    question_id: int
    value_answer_id: int = None
    value_text_box: str = None
    value_tickbox: bool = None
