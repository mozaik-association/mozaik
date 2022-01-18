# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.pydantic import models, utils


class MembershipRequestInfo(models.BaseModel):
    id: int

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
