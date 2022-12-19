# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info(
        "Clean addresses having city but no city_id and no city_man: "
        "Copy 'city' field in 'city_man' column"
    )
    cr.execute(
        """
        UPDATE address_address
        SET city_man=city
        WHERE city_id IS NULL and city_man IS NULL AND city IS NOT NULL;
        """
    )

    _logger.info("Re-compute technical names of all addresses.")
    _logger.info("--------- This may take several minutes -----------")

    env = api.Environment(cr, SUPERUSER_ID, {})
    env["address.address"].with_context(active_test=False).search(
        []
    )._compute_integral_address()

    # Temporarily remove unicity constraint
    cr.execute(
        """
        DROP INDEX address_address_unique_idx"""
    )
    # Flush recomputed technical names in DB to perform following queries.
    env["base"].flush()

    # Search addresses that are duplicates
    # (having the same tuple (technical name, sequence))
    # to clean them

    cr.execute(
        """
    SELECT technical_name
    FROM address_address
    GROUP BY technical_name, sequence
    HAVING COUNT(*) > 1;
    """
    )

    technical_names = cr.fetchall()
    _logger.info("Duplicate addresses " "to proceed: %s items" % len(technical_names))
    for res in technical_names:
        technical_name = res[0]
        cr.execute(
            "SELECT id "
            "FROM address_address "
            "WHERE technical_name = %s ORDER BY id",
            (technical_name,),
        )
        address_res = cr.fetchall()
        address_ids = tuple([address[0] for address in address_res])
        # Find partners that must move: partners having
        # one of the addresses that will be deleted
        cr.execute(
            "SELECT id "
            "FROM res_partner "
            "WHERE address_address_id in %s "
            "AND address_address_id != %s",
            (address_ids, address_ids[0]),
        )

        # Partners to move, depending on if they are in a co-residency or not
        partner_res = cr.fetchall()
        partner_ids = tuple([partner[0] for partner in partner_res])
        partners_cores_ids = (
            env["res.partner"].browse(partner_ids).filtered("co_residency_id").ids
        )
        partners_no_cores_ids = list(
            set(partner_ids).difference(set(partners_cores_ids))
        )

        if partners_cores_ids:
            # Partners in a co-residency: move_co_residency must be TRUE
            _logger.info(
                "Change address_address_id for partners "
                "having a co-residency %(partners_cores_ids)s: "
                "address ids %(old_add_ids)s -> address id %(new_add_id)s"
                % {
                    "partners_cores_ids": partners_cores_ids,
                    "old_add_ids": address_ids[1:],
                    "new_add_id": address_ids[0],
                }
            )
            wiz = env["change.address"].create(
                {
                    "address_id": address_ids[0],
                    "partner_ids": [(6, 0, list(partners_cores_ids))],
                    "move_co_residency": True,
                    "update_instance": False,
                }
            )
            wiz.doit()
            env["base"].flush()

        if partners_no_cores_ids:
            # Partners NOT in a co-residency: move_co_residency must be FALSE
            _logger.info(
                "Change address_address_id for partners "
                "not in a co-residency %(partners_no_cores_ids)s: "
                "address ids %(old_add_ids)s -> address id %(new_add_id)s"
                % {
                    "partners_no_cores_ids": partners_no_cores_ids,
                    "old_add_ids": address_ids[1:],
                    "new_add_id": address_ids[0],
                }
            )
            wiz = env["change.address"].create(
                {
                    "address_id": address_ids[0],
                    "partner_ids": [(6, 0, list(partners_no_cores_ids))],
                    "move_co_residency": False,
                    "update_instance": False,
                }
            )
            wiz.doit()
            env["base"].flush()

        # Delete addresses
        cr.execute(
            """
            DELETE FROM address_address
            WHERE id in %s
            """,
            (address_ids[1:],),
        )

    # Set the unicity constraint again
    cr.execute(
        """
        CREATE UNIQUE INDEX address_address_unique_idx
        ON address_address (technical_name, sequence)
        WHERE (active='t');
        """
    )
