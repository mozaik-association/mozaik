# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    # Specific migration for "Les engagés" existing sponsorship plan.
    sponsorship_product = (
        env["product.template"]
        .with_context(lang="fr_FR")
        .search([("name", "=", "Membre parrainé")])
    )
    sponsorship_product.write({"is_sponsorship_product": True})
