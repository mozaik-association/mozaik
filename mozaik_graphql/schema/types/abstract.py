# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from odoo.addons.graphql_base import OdooObjectType


class AbstractObject(OdooObjectType):
    ID = graphene.String(required=True)
    write_date = graphene.DateTime(required=True)

    def resolve_ID(root, info):
        return root.id
