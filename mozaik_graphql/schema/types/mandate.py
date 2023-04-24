# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from .abstract import AbstractObject
from .assembly import ExtAssembly, IntAssembly, StaAssembly
from .instance import IntInstance
from .legislature import Legislature
from .mandate_category import MandateCategory
from .partner import Partner
from .thesaurus_term import ThesaurusTerm


class AbstractMandate(AbstractObject):
    partner = graphene.Field(Partner, required=True)
    mandate_category = graphene.Field(MandateCategory, required=True)
    start_date = graphene.DateTime(required=True)
    deadline_date = graphene.DateTime(required=True)
    end_date = graphene.DateTime()
    no_show_on_website = graphene.Boolean()
    notes = graphene.String()

    def resolve_partner(root, info):
        return root.partner_id

    def resolve_mandate_category(root, info):
        return root.mandate_category_id

    def resolve_competencies(root, info):
        return root.competencies_m2m_ids or None


class IntMandate(AbstractMandate):
    int_assembly = graphene.Field(IntAssembly, required=True)
    mandate_instance = graphene.Field(IntInstance)

    def resolve_int_assembly(root, info):
        return root.int_assembly_id or None

    def resolve_mandate_instance(root, info):
        return root.mandate_instance_id or None


class ExtMandate(AbstractMandate):
    ext_assembly = graphene.Field(ExtAssembly, required=True)
    competencies = graphene.List(graphene.NonNull(ThesaurusTerm))

    def resolve_ext_assembly(root, info):
        return root.ext_assembly_id or None


class StaMandate(AbstractMandate):
    sta_assembly = graphene.Field(StaAssembly, required=True)
    legislature = graphene.Field(Legislature, required=True)
    competencies = graphene.List(graphene.NonNull(ThesaurusTerm))

    def resolve_ID(root, info):
        return root.id

    def resolve_sta_assembly(root, info):
        return root.sta_assembly_id or None

    def resolve_legislature(root, info):
        return root.legislature_id
