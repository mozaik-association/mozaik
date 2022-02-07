# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from .abstract import AbstractObject
from .city import City
from .country import Country


class Address(AbstractObject):
    street = graphene.String()
    street2 = graphene.String()
    number = graphene.String()
    box = graphene.String()
    city = graphene.Field(City)
    country = graphene.Field(Country, required=True)

    def resolve_street(root, info):
        return root.street_man or None

    def resolve_city(root, info):
        return root.city_id or None

    def resolve_country(root, info):
        return root.country_id or None
