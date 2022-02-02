# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.pydantic import models


class CountrySearchFilter(models.BaseModel):

    id: int = None
    name: str = None
    code: str = None
