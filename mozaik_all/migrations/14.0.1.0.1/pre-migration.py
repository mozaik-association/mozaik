# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from mozaik_survey_is_private.hook import pre_init_hook


def migrate(cr, version):
    pre_init_hook(cr)
