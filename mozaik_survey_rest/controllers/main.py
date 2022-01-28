# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.controllers import main


class SurveyRestController(main.RestController):
    _root_path = "/rest_api/survey/"
    _collection_name = "survey.rest.services"
    _default_auth = "public"
