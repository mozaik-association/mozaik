# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from . import assembly, instance, power_level
from .abstract import AbstractObject


class ElectoralDistrict(AbstractObject):
    name = graphene.String(required=True)
    int_instance = graphene.Field(lambda: instance.IntInstance)
    sta_instance = graphene.Field(lambda: instance.StaInstance)
    assembly = graphene.Field(lambda: assembly.StaAssembly)
    power_level = graphene.Field(lambda: power_level.StaPowerLevel)

    def resolve_int_instance(root, info):
        return root.int_instance_id or None

    def resolve_sta_instance(root, info):
        return root.sta_instance_id or None

    def resolve_assembly(root, info):
        return root.assembly_id or None

    def resolve_power_level(root, info):
        return root.power_level_id or None


electoral_districts = graphene.List(
    graphene.NonNull(ElectoralDistrict),
    required=True,
    description="All electoral districts",
    ids=graphene.List(graphene.Int, description="Search on list of IDs"),
    name=graphene.String(
        description="Case insensitive search by name. %% is supported."
    ),
    limit=graphene.Int(),
    offset=graphene.Int(),
)


def resolve_electoral_districts(info, ids=None, name=None, limit=None, offset=0):
    domain = []
    if ids:
        domain.append(("id", "in", ids))
    if name:
        domain.append(("name", "=ilike", name))
    res = info.context["env"]["electoral.district"].search(
        domain, limit=limit, offset=offset
    )
    return res
