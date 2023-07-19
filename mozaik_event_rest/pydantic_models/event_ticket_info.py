# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from datetime import date, datetime

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils


class EventTicketInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    event_id: int
    name: str
    description: str = None
    start_sale_date: date = None
    end_sale_date: date = None
    seats_available: int = None
    write_date: datetime
    price: float = None

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
