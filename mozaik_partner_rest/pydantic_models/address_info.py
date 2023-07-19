# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.mozaik_country_rest.pydantic_models.country_info import CountryInfo
from odoo.addons.pydantic import utils


class LocalStreetInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    local_street: str
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class AddressInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    country: CountryInfo = pydantic.Field(..., alias="country_id")
    local_street: LocalStreetInfo = pydantic.Field(
        None, alias="address_local_street_id"
    )
    street_man: str = None
    street2: str = None
    number: str = None
    box: str = None
    zip: str = None
    city: str = None
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
