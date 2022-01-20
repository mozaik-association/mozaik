# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if openupgrade.column_exists(cr, "res_partner", "birth_date"):
        cr.execute(
            """
          UPDATE res_partner
          SET birthdate_date=birth_date
          """
        )
