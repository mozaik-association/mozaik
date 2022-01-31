# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.pydantic import models


class PetitionSearchFilter(models.BaseModel):
    is_private: bool = None
    internal_instance_id: int = None
    visible_on_website: bool = None
    date_publish: str = None
