# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from psycopg2.extensions import AsIs

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _get_query():
    """
    Builds the query for obtaining records that have no owner, or only archived owners
    """
    return """
    SELECT id
    FROM %(table_name)s
    WHERE
        id NOT IN
        (SELECT DISTINCT %(record_name)s
        FROM %(m2m_rel_name)s
        WHERE
          %(user_col_name)s IN
          (SELECT id
          FROM res_users
          WHERE active=True
          )
        );
    """


def _update_owners(cr, query, query_params, admin_id):
    cr.execute(query, query_params)
    for value in cr.fetchall():
        cr.execute(
            """
            INSERT INTO %(m2m_rel_name)s
            VALUES (%(record_id)s, %(admin_id)s);
            """,
            {
                "record_id": value[0],
                "admin_id": admin_id,
                "m2m_rel_name": query_params["m2m_rel_name"],
            },
        )


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    admin_id = env.ref("base.user_admin").id
    query = _get_query()

    _logger.info("Add admin as owner on mail templates without active owner")
    query_params = {
        "table_name": AsIs("mail_template"),
        "record_name": AsIs("template_id"),
        "m2m_rel_name": AsIs("email_template_res_users_rel"),
        "user_col_name": AsIs("user_id"),
    }
    _update_owners(cr, query, query_params, admin_id)

    _logger.info("Add admin as owner on involvement categories without active owner")
    query_params = {
        "table_name": AsIs("partner_involvement_category"),
        "record_name": AsIs("category_id"),
        "m2m_rel_name": AsIs("involvement_category_res_users_rel"),
        "user_col_name": AsIs("user_id"),
    }
    _update_owners(cr, query, query_params, admin_id)

    _logger.info("Add admin as owner on distribution lists without active owner")
    query_params = {
        "table_name": AsIs("distribution_list"),
        "record_name": AsIs("dist_list_id"),
        "m2m_rel_name": AsIs("dist_list_res_users_rel"),
        "user_col_name": AsIs("res_users_id"),
    }
    _update_owners(cr, query, query_params, admin_id)
