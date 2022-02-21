# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.addons.event_rest_api.pydantic_models.event_ticket_info import (
    EventTicketInfo as BaseEventTicketInfo,
)


class EventTicketInfo(BaseEventTicketInfo, extends=BaseEventTicketInfo):
    price: float = None
