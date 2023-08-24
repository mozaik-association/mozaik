# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# Disable E0213 because resolvers are staticmethod in disguise
# pylint: disable=no-self-argument
# Disable flake8 on all file in order to disable B902.
# Unfortunately not possible to disable only a specific warning for the whole file
# flake8: noqa

import graphene

from .types.candidature import (
    int_candidatures,
    resolve_int_candidatures,
    resolve_sta_candidatures,
    sta_candidatures,
)
from .types.city import cities, resolve_cities
from .types.electoral_district import electoral_districts, resolve_electoral_districts
from .types.environment import Environment
from .types.instance import int_instances, resolve_int_instances
from .types.membership_line import membership_lines, resolve_membership_lines
from .types.partner import partners, resolve_partners
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
from .types.selection_committee import (
    int_selection_committees,
    resolve_int_selection_committees,
    resolve_sta_selection_committees,
    sta_selection_committees,
)


class Query(graphene.ObjectType):
    environment = graphene.Field(
        Environment, description="Information about the server."
    )
    int_power_levels = int_power_levels
    sta_power_levels = sta_power_levels
    int_instances = int_instances
    int_representatives = int_representatives
    ext_representatives = ext_representatives
    sta_representatives = sta_representatives
    int_candidatures = int_candidatures
    sta_candidatures = sta_candidatures
    int_selection_committees = int_selection_committees
    sta_selection_committees = sta_selection_committees
    electoral_districts = electoral_districts
    cities = cities
    partners = partners
    membership_lines = membership_lines

    def resolve_environment(root, info):
        return Environment()

    def resolve_int_representatives(root, info, limit=None, offset=0):
        return resolve_int_representatives(info, limit, offset)

    def resolve_ext_representatives(root, info, limit=None, offset=0):
        return resolve_ext_representatives(info, limit, offset)

    def resolve_sta_representatives(root, info, limit=None, offset=0):
        return resolve_sta_representatives(info, limit, offset)

    def resolve_int_candidatures(root, info, limit=None, offset=0):
        return resolve_int_candidatures(info, limit, offset)

    def resolve_sta_candidatures(root, info, limit=None, offset=0):
        return resolve_sta_candidatures(info, limit, offset)

    def resolve_int_selection_committees(root, info, limit=None, offset=0):
        return resolve_int_selection_committees(info, limit, offset)

    def resolve_sta_selection_committees(root, info, limit=None, offset=0):
        return resolve_sta_selection_committees(info, limit, offset)

    def resolve_int_power_levels(root, info, ids=None, name=None, limit=None, offset=0):
        return resolve_int_power_levels(info, ids, name, limit, offset)

    def resolve_sta_power_levels(root, info, ids=None, name=None, limit=None, offset=0):
        return resolve_sta_power_levels(info, ids, name, limit, offset)

    def resolve_int_instances(root, info, ids=None, name=None, limit=None, offset=0):
        return resolve_int_instances(info, ids, name, limit, offset)

    def resolve_electoral_districts(
        root, info, ids=None, name=None, limit=None, offset=0
    ):
        return resolve_electoral_districts(info, ids, name, limit, offset)

    def resolve_cities(
        root, info, ids=None, name=None, zipcode=None, limit=None, offset=0
    ):
        return resolve_cities(info, ids, name, zipcode, limit, offset)

    def resolve_partners(
        root, info, ids=None, name=None, activeTest=None, limit=None, offset=0
    ):
        return resolve_partners(info, ids, name, activeTest, limit, offset)

    def resolve_membership_lines(
        root,
        info,
        ids=None,
        minPrice=0,
        dateFromAfter=None,
        dateToBefore=None,
        regularizationDateAfter=None,
        regularizationDateBefore=None,
        activeTest=None,
        limit=None,
        offset=0,
    ):
        return resolve_membership_lines(
            info,
            ids,
            minPrice,
            dateFromAfter,
            dateToBefore,
            regularizationDateAfter,
            regularizationDateBefore,
            activeTest,
            limit,
            offset,
        )


schema = graphene.Schema(query=Query)
