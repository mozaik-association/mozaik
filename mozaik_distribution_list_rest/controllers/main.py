# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.controllers import main


class DistributionListRestController(main.RestController):
    _root_path = "/rest_api/distribution_list/"
    _collection_name = "distribution.list.rest.services"
    _default_auth = "public"
