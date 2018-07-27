# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, tools, _


class EmailCoordinate(models.Model):
    _name = 'email.coordinate'
    _inherit = ['abstract.coordinate']
    _description = "Email Coordinate"

    _mail_mass_mailing = _('Email Coordinate')
    _mail_post_access = 'read'
    _discriminant_field = 'email'
    _undo_redirect_action = 'mozaik_email.email_coordinate_action'
    _unicity_keys = 'partner_id, email'
    _rec_name = _discriminant_field

    email = fields.Char(
        required=True,
        index=True,
    )

    @api.multi
    @api.constrains('email')
    def _check_email(self):
        """
        Constrain function to check if the email format is valid
        """
        bad_records = self.filtered(
            lambda r: not tools.single_email_re.match(r.email))
        bad_records = bad_records.with_prefetch(self._prefetch)
        if bad_records:
            details = "\n- ".join(bad_records.mapped("email"))
            message = _("These email addresses are invalid:\n- %s") % details
            raise exceptions.ValidationError(message)

    @api.model
    def check_mail_message_access(self, res_ids, operation, model_name=None):
        """
        :param res_ids: list of int
        :param operation: str
        :param model_name: str
        """
        context = self.env.context
        if context.get('active_model') == 'distribution.list' and \
                context.get('main_target_model') == 'email.coordinate':
            return None
        return super().check_mail_message_access(
            res_ids=res_ids, operation=operation, model_name=model_name)
