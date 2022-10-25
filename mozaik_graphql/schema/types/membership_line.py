# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from .abstract import AbstractObject
from .partner import Partner


class MembershipLine(AbstractObject):
    ID = graphene.Int()
    active = graphene.Boolean()
    price = graphene.Float()
    price_paid = graphene.Float()
    date_from = graphene.Date()
    date_to = graphene.Date()
    regularization_date = graphene.Date()
    partner = graphene.Field(Partner)

    def resolve_ID(root, info):
        return root.id

    def resolve_partner(root, info):
        return root.partner_id


membership_lines = graphene.List(
    graphene.NonNull(MembershipLine),
    required=True,
    description="All membership lines",
    ids=graphene.List(graphene.Int, description="Search on list of IDs"),
    minPrice=graphene.Argument(graphene.Float, description="Minimum price (included)"),
    dateFromAfter=graphene.Argument(graphene.Date, description="Date from after..."),
    dateToBefore=graphene.Argument(graphene.Date, description="Date to before..."),
    regularizationDateAfter=graphene.Argument(
        graphene.Date, description="Regularization date after..."
    ),
    regularizationDateBefore=graphene.Argument(
        graphene.Date, description="Regularization date before..."
    ),
    activeTest=graphene.Argument(
        graphene.Boolean,
        description="True if you want only active records, False otherwise",
    ),
    limit=graphene.Int(),
    offset=graphene.Int(),
)


def resolve_membership_lines(
    info,
    ids=None,
    minPrice=0,
    dateFromAfter=None,
    dateToBefore=None,
    regularizationDateAfter=None,
    regularizationDateBefore=None,
    activeTest=None,
    limit=None,
    offset=0,
):
    domain = [("price", ">=", minPrice)]
    if minPrice == 0 or minPrice is None:
        # add also membership lines for which price is null.
        domain = ["|"] + domain + [("price", "=", False)]
    if ids:
        domain.append(("id", "in", ids))
    if dateFromAfter:
        domain.append(("date_from", ">=", dateFromAfter))
    if dateToBefore:
        domain.append(("date_to", "<=", dateToBefore))
    if regularizationDateAfter:
        domain.append(("regularization_date", ">=", regularizationDateAfter))
    if regularizationDateBefore:
        domain.append(("regularization_date", "<=", regularizationDateBefore))
    activeTest = activeTest if activeTest is not None else True
    res = (
        info.context["env"]["membership.line"]
        .with_context(active_test=activeTest)
        .search(domain, limit=limit, offset=offset)
    )
    return res
