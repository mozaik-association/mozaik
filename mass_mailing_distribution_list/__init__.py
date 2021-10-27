# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import models
from . import wizards
from odoo.api import Environment
from odoo import SUPERUSER_ID


def _create_mail_alias(cr):

    cr.execute("ALTER TABLE distribution_list ADD COLUMN alias_id INTEGER;")

    env = Environment(cr, SUPERUSER_ID, {"active_test": False})
    dist_model = env.ref("distribution_list.model_distribution_list")
    for distribution_list in env["distribution.list"].search([]):
        alias = env["mail.alias"].create(
            {
                "alias_parent_model_id": dist_model.id,
                "alias_model_id": dist_model.id,
                "alias_defaults": {"distribution_list_id": distribution_list.id},
            }
        )
        cr.execute(
            "UPDATE distribution_list SET alias_id=%(alias_id)s WHERE id=%(dist_id)s",
            {"alias_id": alias.id, "dist_id": distribution_list.id},
        )
