# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from .abstract import AbstractObject
from .membership_state import MembershipState


class Partner(AbstractObject):
    name = graphene.String()
    firstname = graphene.String()
    lastname = graphene.String()
    gender = graphene.String()
    email = graphene.String()
    membership_state = graphene.Field(MembershipState)

    def resolve_membership_state(root, info):
        return root.membership_state_id or None
