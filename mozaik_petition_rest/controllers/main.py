# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.controllers import main


class PetitionRestController(main.RestController):
    _root_path = "/rest_api/petition/"
    _collection_name = "petition.rest.services"
    _default_auth = "public"
