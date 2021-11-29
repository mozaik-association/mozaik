# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.controllers import main


class EventRestController(main.RestController):
    _root_path = "/rest_api/event/"
    _collection_name = "event.rest.services"
    _default_auth = "public"
