============================================
Mozaik Membership Request Autovalidate Light
============================================

This module introduces a second way of auto-validating membership requests.

Up to now, with the basic membership request addons (`mozaik_membership_request` and `mozaik_membership_request_autovalidate`),
it was possible to auto-validate a membership request under certain conditions.
If the membership request was auto-validated, all the data on the membership request were copied on the partner.

The goal of this light auto-validation is to, under certain conditions, only copy part of the membership request data.

Technically, a membership request is eligible for light auto-validation if:
* The light auto-validation mechanism was asked on the membership request, and
* Certain specific conditions are met. These conditions are defined in `_check_light_autoval` and may be overridden to let each party chose them.

In this case, the membership request will be duplicated. Only the info that must be copied on the partner are copied on the duplicated membership request.
The initial membership request won't be validated, it will go into a new state "Treated via light auto-validation" as soon as the duplicated membership request will be validated.
A link is added between both membership requests to let the user understand the process.

The info that are copied in the light membership request are the following:
* Involvements
* Indexation & comments
* Address (under specific cases only, see `_prepare_address_vals_for_light_mr`)
