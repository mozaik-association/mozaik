# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=no-self-argument
# flake8: noqa

import graphene

from .abstract import AbstractObject


class ThesaurusTerm(AbstractObject):
    name = graphene.String(required=True)
