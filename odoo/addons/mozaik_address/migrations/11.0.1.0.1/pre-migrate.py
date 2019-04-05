# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Add postal_coordinate_id column")
    cr.execute(
        """
        ALTER TABLE res_partner ADD postal_coordinate_id INTEGER
        """)
    cr.execute(
        """
        ALTER TABLE res_partner ADD FOREIGN KEY (postal_coordinate_id) 
        REFERENCES postal_coordinate (id)
        """)
    _logger.info("updating postal_coordinate_id column")
    cr.execute(
        """
        UPDATE res_partner AS rp SET postal_coordinate_id = pc.id
         FROM postal_coordinate AS pc WHERE pc.partner_id = rp.id AND pc.is_main IS TRUE AND pc.active IS TRUE
        """)
