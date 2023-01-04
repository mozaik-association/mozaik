# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from odoo.http import request

from .abstract import AbstractObject
from .address import Address
from .instance import IntInstance
from .membership_state import MembershipState


class Partner(AbstractObject):
    name = graphene.String()
    firstname = graphene.String()
    lastname = graphene.String()
    gender = graphene.String()
    email = graphene.String()
    identifier = graphene.String()
    phone = graphene.String()
    mobile = graphene.String()
    mandate_email = graphene.String()
    mandate_phone = graphene.String()
    address = graphene.Field(Address)
    int_instances = graphene.List(graphene.NonNull(IntInstance))
    membership_state = graphene.Field(MembershipState)
    social_twitter = graphene.String()
    social_facebook = graphene.String()
    social_youtube = graphene.String()
    social_linkedin = graphene.String()
    social_instagram = graphene.String()
    website = graphene.String()
    secondary_website = graphene.String()
    image_url = graphene.String()
    no_show_mandates = graphene.Boolean()
    is_deceased = graphene.Boolean()
    membership_card_sent = graphene.Boolean()
    membership_card_sent_date = graphene.Date()

    def resolve_membership_state(root, info):
        return root.membership_state_id or None

    def resolve_address(root, info):
        return root.address_address_id or None

    def resolve_int_instances(root, info):
        return root.int_instance_ids or None

    def resolve_image_url(root, info):
        return "%sweb/image_api/res.partner/%d/image_1920" % (
            request.httprequest.host_url,
            root.id,
        )


partners = graphene.List(
    graphene.NonNull(Partner),
    required=True,
    description="All partners",
    ids=graphene.List(graphene.Int, description="Search on list of IDs"),
    name=graphene.String(
        description="Case insensitive search by name. %% is supported."
    ),
    activeTest=graphene.Argument(
        graphene.Boolean,
        description="True if you want only active records, False otherwise",
    ),
    limit=graphene.Int(),
    offset=graphene.Int(),
)


def resolve_partners(info, ids=None, name=None, activeTest=None, limit=None, offset=0):
    domain = []
    if ids:
        domain.append(("id", "in", ids))
    if name:
        domain.append(("name", "=ilike", name))
    activeTest = activeTest if activeTest is not None else True
    res = (
        info.context["env"]["res.partner"]
        .with_context(active_test=activeTest)
        .search(domain, limit=limit, offset=offset)
    )
    return res
