# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from odoo.http import request

from .abstract import AbstractObject
from .address import Address
from .membership_state import MembershipState


class Partner(AbstractObject):
    name = graphene.String()
    firstname = graphene.String()
    lastname = graphene.String()
    gender = graphene.String()
    email = graphene.String()
    mandate_email = graphene.String()
    mandate_phone = graphene.String()
    address = graphene.Field(Address)
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

    def resolve_membership_state(root, info):
        return root.membership_state_id or None

    def resolve_address(root, info):
        return root.address_address_id or None

    def resolve_image_url(root, info):
        return "%sweb/image_api/res.partner/%d/image_1920" % (
            request.httprequest.host_url,
            root.id,
        )
