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
    assemblies = graphene.List(graphene.NonNull(lambda: assembly.IntAssembly))
    electoral_districts = graphene.List(
        graphene.NonNull(lambda: electoral_district.ElectoralDistrict)
    )


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
