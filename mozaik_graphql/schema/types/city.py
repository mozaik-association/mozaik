# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from .abstract import AbstractObject
from .country import Country


class City(AbstractObject):
    name = graphene.String(required=True)
    zipcode = graphene.String(required=True)
    country = graphene.Field(Country, required=True)

    def resolve_country(root, info):
        return root.country_id or None
