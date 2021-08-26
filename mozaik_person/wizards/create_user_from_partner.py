# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _


class CreateUserFromPartner(models.TransientModel):

    _name = 'create.user.from.partner'
    _description = 'Wizard to Create a User from a Partner'

    nok = fields.Char(
        string='Reason',
        default=False,
        readonly=True,
    )
    login = fields.Char(
        required=True,
    )
    role_id = fields.Many2one(
        comodel_name='res.users.role',
        string="User's role",
        required=True,
        ondelete='cascade',
    )

    @api.model
    def default_get(self, fields_list):
        """
        Get default values for the wizard.
        Compute the reason for which the wizard is not working
        :raise: ERROR if no active_id found in the context
        """
        partner_id = self._context.get('active_id', False) or False
        if not partner_id:
            raise exceptions.UserError(
                _('A partner is required to create a new user!'))

        res = super().default_get(fields_list)

        partner = self.env['res.partner'].browse([partner_id])

        if 'nok' in fields_list:
            nok = False
            if partner.user_ids:
                nok = 'user'
            elif not partner.active:
                nok = 'active'
            elif partner.is_company and not partner.is_assembly:
                nok = 'company'

            res.update({'nok': nok})

        return res

    def create_user_from_partner(self):
        """
        Create a user based on the selected partner (active_id) and associate
        it to the choosen role
        """
        self.ensure_one()

        partner_id = self._context.get('active_id', False)
        partner = self.env['res.partner'].browse([partner_id])

        role_id = self.role_id
        login = self.login

        return partner._create_user(login, role_id)
