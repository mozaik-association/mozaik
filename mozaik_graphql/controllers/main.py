# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http

from odoo.addons.graphql_base import GraphQLControllerMixin

from ..schema.main import schema

GRAPHIQL_PATH = "/graphiql/api"


class GraphQLController(http.Controller, GraphQLControllerMixin):
    @http.route(GRAPHIQL_PATH, auth="user")
    def graphiql(self, **kwargs):
        return self._handle_graphiql_request(schema.graphql_schema)
