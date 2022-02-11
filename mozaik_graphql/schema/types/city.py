# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from .abstract import AbstractObject
from .country import Country
from .instance import IntInstance


class City(AbstractObject):
    name = graphene.String(required=True)
    zipcode = graphene.String(required=True)
    country = graphene.Field(Country, required=True)
    int_instance = graphene.Field(IntInstance, required=True)

    def resolve_country(root, info):
        return root.country_id or None

    def resolve_int_instance(root, info):
        return root.int_instance_id or None


cities = graphene.List(
    graphene.NonNull(City),
    required=True,
    description="All cities",
    ids=graphene.List(graphene.Int, description="Search on list of IDs"),
    name=graphene.String(
        description="Case insensitive search by name. %% is supported."
    ),
    zipcode=graphene.String(description="Search by zipcode. %% is supported."),
    limit=graphene.Int(),
    offset=graphene.Int(),
)


def resolve_cities(info, ids=None, name=None, zipcode=None, limit=None, offset=0):
    domain = []
    if ids:
        domain.append(("id", "in", ids))
    if name:
        domain.append(("name", "=ilike", name))
    if zipcode:
        domain.append(("zipcode", "=ilike", zipcode))
    res = info.context["env"]["res.city"].search(domain, limit=limit, offset=offset)
    return res
