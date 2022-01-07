# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from . import power_level
from .abstract import AbstractObject
from .mandate_category import MandateCategory


class AbstractAssemblyCategory(AbstractObject):
    name = graphene.String(required=True)
    mandate_categories = graphene.List(graphene.NonNull(MandateCategory))

    def resolve_power_level(root, info):
        return root.power_level_id or None

    def resolve_mandate_categories(root, info):
        return root.mandate_category_ids or None


class IntAssemblyCategory(AbstractAssemblyCategory):
    power_level = graphene.Field(lambda: power_level.IntPowerLevel)


class ExtAssemblyCategory(AbstractAssemblyCategory):
    pass


class StaAssemblyCategory(AbstractAssemblyCategory):
    power_level = graphene.Field(lambda: power_level.StaPowerLevel)
