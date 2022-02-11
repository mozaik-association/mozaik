# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from . import assembly_category
from .abstract import AbstractObject


class AbstractPowerLevel(AbstractObject):
    name = graphene.String(required=True)

    def resolve_assembly_categories(root, info):
        return root.assembly_category_ids or None


class IntPowerLevel(AbstractPowerLevel):
    assembly_categories = graphene.List(
        graphene.NonNull(lambda: assembly_category.IntAssemblyCategory)
    )


int_power_levels = graphene.List(
    graphene.NonNull(IntPowerLevel),
    required=True,
    description="All internal power levels",
    ids=graphene.List(graphene.Int, description="Search on list of IDs"),
    name=graphene.String(
        description="Case insensitive search by name. %% is supported."
    ),
    limit=graphene.Int(),
    offset=graphene.Int(),
)


def resolve_int_power_levels(info, ids=None, name=None, limit=None, offset=0):
    domain = []
    if ids:
        domain.append(("id", "in", ids))
    if name:
        domain.append(("name", "=ilike", name))
    res = info.context["env"]["int.power.level"].search(
        domain, limit=limit, offset=offset
    )
    return res


class StaPowerLevel(AbstractPowerLevel):
    assembly_categories = graphene.List(
        graphene.NonNull(lambda: assembly_category.StaAssemblyCategory)
    )


sta_power_levels = graphene.List(
    graphene.NonNull(StaPowerLevel),
    required=True,
    description="All state power levels",
    ids=graphene.List(graphene.Int, description="Search on list of IDs"),
    name=graphene.String(
        description="Case insensitive search by name. %% is supported."
    ),
    limit=graphene.Int(),
    offset=graphene.Int(),
)


def resolve_sta_power_levels(info, ids=None, name=None, limit=None, offset=0):
    domain = []
    if ids:
        domain.append(("id", "in", ids))
    if name:
        domain.append(("name", "=ilike", name))
    res = info.context["env"]["sta.power.level"].search(
        domain, limit=limit, offset=offset
    )
    return res
