# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import Optional

from extendable_pydantic import ExtendableModelMeta  # pylint:disable=W7936
from pydantic import BaseModel  # pylint:disable=W7936

from odoo.addons.pydantic import utils


class PartnerMin(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    name: str
    street: Optional[str] = None
    zip: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
