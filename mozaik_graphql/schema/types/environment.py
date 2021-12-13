# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

import odoo


class Environment(graphene.ObjectType):
    name = graphene.String(required=True)
    version = graphene.String(required=True)
    database = graphene.String(required=True)
    error_simulation = graphene.String(
        description="Fetching this will simulate a runtime error."
    )

    def resolve_name(root, info):
        return odoo.tools.config["running_env"]

    def resolve_version(root, info):
        return (
            info.context["env"]["ir.module.module"]
            .search([("name", "=", "mozaik_all")])
            .installed_version
        )

    def resolve_database(root, info):
        return info.context["env"].cr.dbname

    def resolve_error_simulation(root, info):
        raise RuntimeError("Runtime error simulation")
