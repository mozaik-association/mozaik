# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from .abstract import AbstractObject
from .power_level import StaPowerLevel


class Legislature(AbstractObject):
    name = graphene.String(required=True)
    power_level = graphene.Field(StaPowerLevel, required=True)

    def resolve_power_level(root, info):
        return root.power_level_id
