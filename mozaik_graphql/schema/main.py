# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# Disable E0213 because resolvers are staticmethod in disguise
# pylint: disable=no-self-argument
# Disable flake8 on all file in order to disable B902.
# Unfortunately not possible to disable only a specific warning for the whole file
# flake8: noqa

import graphene

from .types.city import cities, resolve_cities
from .types.environment import Environment
from .types.power_level import (
    int_power_levels,
    resolve_int_power_levels,
    resolve_sta_power_levels,
    sta_power_levels,
)
from .types.representative import (
    ext_representatives,
    int_representatives,
    resolve_ext_representatives,
    resolve_int_representatives,
    resolve_sta_representatives,
    sta_representatives,
)


class Query(graphene.ObjectType):
    environment = graphene.Field(
        Environment, description="Information about the server."
    )
    int_power_levels = int_power_levels
    sta_power_levels = sta_power_levels
    int_representatives = int_representatives
    ext_representatives = ext_representatives
    sta_representatives = sta_representatives
    cities = cities

    def resolve_environment(root, info):
        return Environment()

    def resolve_int_representatives(root, info, limit=None, offset=0):
        return resolve_int_representatives(info, limit, offset)

    def resolve_ext_representatives(root, info, limit=None, offset=0):
        return resolve_ext_representatives(info, limit, offset)

    def resolve_sta_representatives(root, info, limit=None, offset=0):
        return resolve_sta_representatives(info, limit, offset)

    def resolve_int_power_levels(root, info, ids=None, name=None, limit=None, offset=0):
        return resolve_int_power_levels(info, ids, name, limit, offset)

    def resolve_sta_power_levels(root, info, ids=None, name=None, limit=None, offset=0):
        return resolve_sta_power_levels(info, ids, name, limit, offset)

    def resolve_cities(
        root, info, ids=None, name=None, zipcode=None, limit=None, offset=0
    ):
        return resolve_cities(info, ids, name, zipcode, limit, offset)


schema = graphene.Schema(query=Query)
