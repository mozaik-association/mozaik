# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.controllers import main


class CountryRestController(main.RestController):
    _root_path = "/rest_api/country/"
    _collection_name = "country.rest.services"
    _default_auth = "public"
