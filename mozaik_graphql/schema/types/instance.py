# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from . import assembly, electoral_district
from .abstract import AbstractObject
from .power_level import IntPowerLevel, StaPowerLevel


class AbstractInstance(AbstractObject):
    name = graphene.String(required=True)

    def resolve_power_level(root, info):
        return root.power_level_id

    def resolve_parent(root, info):
        return root.parent_id or None

    def resolve_assemblies(root, info):
        return root.assembly_ids or None

    def resolve_electoral_districts(root, info):
        return root.electoral_district_ids or None


class IntInstance(AbstractInstance):
    power_level = graphene.Field(IntPowerLevel, required=True)
    parent = graphene.Field(lambda: IntInstance)
    code = graphene.String()
    sta_instances = graphene.List(graphene.NonNull(lambda: StaInstance))
    assemblies = graphene.List(graphene.NonNull(lambda: assembly.IntAssembly))
    electoral_districts = graphene.List(
        graphene.NonNull(lambda: electoral_district.ElectoralDistrict)
    )
    ref_partner_ref_mandate = graphene.String()

    def resolve_sta_instances(root, info):
        return root.sta_instance_ids or None

    def resolve_ref_partner_ref_mandate(root, info):
        if root.ref_mandate_id:
            return root.ref_mandate_id.partner_id.identifier
        return None


class StaInstance(AbstractInstance):
    power_level = graphene.Field(StaPowerLevel, required=True)
    parent = graphene.Field(lambda: StaInstance)
    secondary_parent = graphene.Field(lambda: StaInstance)
    int_instance = graphene.Field(IntInstance)
    assemblies = graphene.List(graphene.NonNull(lambda: assembly.StaAssembly))
    electoral_districts = graphene.List(
        graphene.NonNull(lambda: electoral_district.ElectoralDistrict)
    )

    def resolve_secondary_parent(root, info):
        return root.secondary_parent_id or None

    def resolve_int_instance(root, info):
        return root.int_instance_id or None


int_instances = graphene.List(
    graphene.NonNull(IntInstance),
    required=True,
    description="All internal instances",
    ids=graphene.List(graphene.Int, description="Search on list of IDs"),
    name=graphene.String(
        description="Case insensitive search by name. %% is supported."
    ),
    limit=graphene.Int(),
    offset=graphene.Int(),
)


def resolve_int_instances(info, ids=None, name=None, limit=None, offset=0):
    domain = []
    if ids:
        domain.append(("id", "in", ids))
    if name:
        domain.append(("name", "=ilike", name))
    res = info.context["env"]["int.instance"].search(domain, limit=limit, offset=offset)
    return res
