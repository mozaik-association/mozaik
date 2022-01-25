# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def string_count(string, pattern):
    """
    If string, use count method.
    If false: returns 0
    """
    if string:
        return string.count(pattern)
    return 0


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Changing mail templates from email.coordinates to res.partner")

    templates = env["mail.template"].search(
        [("model_id.model", "=", "email.coordinate")]
    )

    contact_model = env["ir.model"].search([("model", "=", "res.partner")])
    successful_template_ids = []

    for template in templates:
        #  Counting number of dynamic placeholders starting with ${object.partner_id
        dynamic_pl_to_partner = string_count(
            template.subject, "${object.partner_id"
        ) + string_count(template.body_html, "${object.partner_id")

        #  Counting the total number of dynamic placeholders
        total_dynamic_pl_subject = string_count(template.subject, "${object")
        total_dynamic_pl_body = string_count(template.body_html, "${object")

        if total_dynamic_pl_subject + total_dynamic_pl_body != dynamic_pl_to_partner:
            _logger.info(
                "Template %s cannot be migrated automatically due to dynamical placeholders"
                % template.name
            )
        else:
            # Replace all dynamic placeholders containing ${object.partner_id
            if template.body_html and total_dynamic_pl_body > 0:
                template.write(
                    {
                        "body_html": template.body_html.replace(
                            "${object.partner_id", "${object"
                        )
                    }
                )
            if template.subject and total_dynamic_pl_subject > 0:
                template.write(
                    {
                        "subject": template.subject.replace(
                            "${object.partner_id", "${object"
                        )
                    }
                )

            # Plan to change model
            successful_template_ids.append(template.id)

    # Change model on all successful templates
    env["mail.template"].browse(successful_template_ids).write(
        {"model_id": contact_model.id}
    )
