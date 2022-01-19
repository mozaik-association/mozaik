# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.map_values(
        cr,
        "civil_status",
        "marital",
        [
            ("s", "separated"),
            ("m", "married"),
            ("u", "unmarried"),
            ("w", "widower"),
            ("d", "divorced"),
        ],
        table="res_partner",
    )
