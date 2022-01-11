# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from .mandate import ExtMandate, IntMandate, StaMandate
from .partner import Partner


class AbstractRepresentative(Partner):
    pass


class IntRepresentative(AbstractRepresentative):
    int_mandates = graphene.List(graphene.NonNull(IntMandate))

    def resolve_int_mandates(root, info):
        return root.int_mandate_ids or None


int_representatives = graphene.List(
    graphene.NonNull(IntRepresentative),
    required=True,
    description="All internal representatives",
    limit=graphene.Int(),
    offset=graphene.Int(),
)


def resolve_int_representatives(info, limit=None, offset=0):
    domain = [("int_mandate_ids", "!=", False)]
    res = info.context["env"]["res.partner"].search(domain, limit=limit, offset=offset)
    return res


class ExtRepresentative(AbstractRepresentative):
    ext_mandates = graphene.List(graphene.NonNull(ExtMandate))

    def resolve_ext_mandates(root, info):
        return root.ext_mandate_ids or None


ext_representatives = graphene.List(
    graphene.NonNull(ExtRepresentative),
    required=True,
    description="All external representatives",
    limit=graphene.Int(),
    offset=graphene.Int(),
)


def resolve_ext_representatives(info, limit=None, offset=0):
    domain = [("ext_mandate_ids", "!=", False)]
    res = info.context["env"]["res.partner"].search(domain, limit=limit, offset=offset)
    return res


class StaRepresentative(AbstractRepresentative):
    sta_mandates = graphene.List(graphene.NonNull(StaMandate))

    def resolve_sta_mandates(root, info):
        return root.sta_mandate_ids or None


sta_representatives = graphene.List(
    graphene.NonNull(StaRepresentative),
    required=True,
    description="All state representatives",
    limit=graphene.Int(),
    offset=graphene.Int(),
)


def resolve_sta_representatives(info, limit=None, offset=0):
    domain = [("sta_mandate_ids", "!=", False)]
    res = info.context["env"]["res.partner"].search(domain, limit=limit, offset=offset)
    return res
