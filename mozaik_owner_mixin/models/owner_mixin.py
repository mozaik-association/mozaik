# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class OwnerMixin(models.AbstractModel):

    _name = "owner.mixin"
    _description = "Mixin to add a m2m field 'owners' on a model"

    res_users_ids = fields.Many2many(
        comodel_name="res.users",
        string="Owners",
        default=lambda self: self._get_default_owner(),
    )

    def _get_default_owner(self):
        """
        Default owner is the current user if active,
        and admin otherwise
        """
        admin = self.env.ref("base.user_admin")
        return self.env.user if self.env.user.active else admin

    @api.constrains("res_users_ids")
    def _check_res_users_ids_not_empty(self):
        """
        res_users_ids is not required otherwise it causes problems
        with record rules on res.partner, but we want at least
        one owner for each record.
        """
        for record in self:
            owners = record.sudo().read(["res_users_ids"])[0]["res_users_ids"]
            if len(owners) == 0:
                raise exceptions.ValidationError(
                    _("Please add a (non archived) owner for this record.")
                )

    def write(self, vals):
        if (
            "res_users_ids" in vals
            and len(vals["res_users_ids"]) == 1
            and vals["res_users_ids"][0][0] == 6
        ):
            res_users_ids_vals = vals["res_users_ids"]
            for record in self:
                # We must take each record separately, to check users
                # that are already present and that have to stay.
                # We want to avoid infinite loops when calling write again,
                # so we use owners_prepared context key.
                # What's more, we must pop res_users_ids from vals before calling
                # super().write(), since values were written on each record
                # separately.
                if not record.env.context.get("owners_prepared", False):
                    users_allowed = record.read(["res_users_ids"])[0]["res_users_ids"]
                    users_sudo = record.sudo().read(["res_users_ids"])[0][
                        "res_users_ids"
                    ]
                    users_not_allowed = list(
                        set(users_sudo) - set(users_allowed)
                    )  # these users have to stay

                    # Add other users
                    users_to_keep = res_users_ids_vals[0][2]
                    users_to_keep = list(set(users_to_keep).union(users_not_allowed))
                    record.with_context(owners_prepared=True).write(
                        {"res_users_ids": [[6, 0, users_to_keep]]}
                    )
                    vals.pop("res_users_ids", False)
        res = super().write(vals)
        return res
