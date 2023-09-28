# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):

    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "mozaik_account.product_template_donation",
                "mozaik_account_donation.product_product_donation",
            )
        ],
        allow_merge=True,
    )
