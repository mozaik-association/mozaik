# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from .abstract import AbstractObject
from .partner import Partner
from .selection_committee import IntSelectionCommittee, StaSelectionCommittee


class AbstractCandidature(AbstractObject):
    partner = graphene.Field(Partner, required=True)
    state = graphene.String(
        required=True,
        description="Possible values: "
        "draft, declared, designated, rejected, elected, non-elected",
    )

    def resolve_partner(root, info):
        return root.partner_id

    def resolve_selection_committee(root, info):
        return root.selection_committee_id


class IntCandidature(AbstractCandidature):
    selection_committee = graphene.Field(IntSelectionCommittee, required=True)


int_candidatures = graphene.List(
    graphene.NonNull(IntCandidature),
    required=True,
    description="All internal candidatures",
    limit=graphene.Int(),
    offset=graphene.Int(),
)


def resolve_int_candidatures(info, limit=None, offset=0):
    domain = []
    res = info.context["env"]["int.candidature"].search(
        domain, limit=limit, offset=offset
    )
    return res


class StaCandidature(AbstractCandidature):
    selection_committee = graphene.Field(StaSelectionCommittee, required=True)
    is_effective = graphene.Boolean()
    list_effective_position = graphene.Int()
    is_substitute = graphene.Boolean()
    list_substitute_position = graphene.Int()
    effective_votes = graphene.Int()


sta_candidatures = graphene.List(
    graphene.NonNull(StaCandidature),
    required=True,
    description="All state candidatures",
    limit=graphene.Int(),
    offset=graphene.Int(),
)


def resolve_sta_candidatures(info, limit=None, offset=0):
    domain = []
    res = info.context["env"]["sta.candidature"].search(
        domain, limit=limit, offset=offset
    )
    return res
