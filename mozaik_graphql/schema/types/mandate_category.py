# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from . import assembly_category
from .abstract import AbstractObject


class MandateCategory(AbstractObject):
    name = graphene.String(required=True)
    female_name = graphene.String(required=True)
    sequence = graphene.Int()
    ext_assembly_category = graphene.Field(
        lambda: assembly_category.ExtAssemblyCategory
    )
    int_assembly_category = graphene.Field(
        lambda: assembly_category.IntAssemblyCategory
    )
    sta_assembly_category = graphene.Field(
        lambda: assembly_category.StaAssemblyCategory
    )

    def resolve_ext_assembly_category(root, info):
        return root.ext_assembly_category_id or None

    def resolve_int_assembly_category(root, info):
        return root.int_assembly_category_id or None

    def resolve_sta_assembly_category(root, info):
        return root.sta_assembly_category_id or None
