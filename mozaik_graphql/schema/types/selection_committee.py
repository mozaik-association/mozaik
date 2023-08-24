# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from . import candidature
from .abstract import AbstractObject
from .assembly import IntAssembly, StaAssembly
from .electoral_district import ElectoralDistrict
from .instance import IntInstance
from .legislature import Legislature
from .mandate_category import MandateCategory


class AbstractSelectionCommittee(AbstractObject):
    name = graphene.String(required=True)
    int_instance = graphene.Field(IntInstance)
    mandate_category = graphene.Field(MandateCategory, required=True)
    mandate_start_date = graphene.Date(required=True)
    mandate_deadline_date = graphene.Date(required=True)
    state = graphene.String(required=True, description="Possible values: draft, done")
    note = graphene.String()
    decision_date = graphene.Date()

    def resolve_assembly(root, info):
        return root.assembly_id or None

    def resolve_int_instance(root, info):
        return root.int_instance_id or None

    def resolve_mandate_category(root, info):
        return root.mandate_category_id or None

    def resolve_candidatures(root, info):
        return root.candidature_ids or None


class IntSelectionCommittee(AbstractSelectionCommittee):
    assembly = graphene.Field(IntAssembly)
    candidatures = graphene.List(graphene.NonNull(lambda: candidature.IntCandidature))


int_selection_committees = graphene.List(
    graphene.NonNull(IntSelectionCommittee),
    required=True,
    description="All internal selection committees",
    limit=graphene.Int(),
    offset=graphene.Int(),
)


def resolve_int_selection_committees(info, limit=None, offset=0):
    domain = []
    res = info.context["env"]["int.selection.committee"].search(
        domain, limit=limit, offset=offset
    )
    return res


class StaSelectionCommittee(AbstractSelectionCommittee):
    electoral_district = graphene.Field(ElectoralDistrict)
    assembly = graphene.Field(StaAssembly)
    legislature = graphene.Field(Legislature)
    listname = graphene.String()
    is_cartel = graphene.Boolean()
    cartel_composition = graphene.String()
    candidatures = graphene.List(graphene.NonNull(lambda: candidature.StaCandidature))

    def resolve_electoral_district(root, info):
        return root.electoral_district_id or None

    def resolve_legislature(root, info):
        return root.legislature_id or None


sta_selection_committees = graphene.List(
    graphene.NonNull(StaSelectionCommittee),
    required=True,
    description="All state selection committees",
    limit=graphene.Int(),
    offset=graphene.Int(),
)


def resolve_sta_selection_committees(info, limit=None, offset=0):
    domain = []
    res = info.context["env"]["sta.selection.committee"].search(
        domain, limit=limit, offset=offset
    )
    return res
