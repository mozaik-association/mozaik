# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import api, exceptions, fields, models, tools, _
from odoo.fields import first
from odoo.tools.config import config as system_base_config

RUNNING_ENV = system_base_config.get('running_env', '')
MASK = (system_base_config.misc.get('ir.config_parameter', {}).get(
    'email.sanitize.mask') or '').replace('%%', '%')
RE_MASK = re.compile(r'^%s$' % re.escape(MASK).replace('\\%s', '.*'))


class EmailCoordinate(models.Model):
    _name = 'email.coordinate'
    _inherit = ['abstract.coordinate']
    _description = "Email Coordinate"

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
        if bad_records:
            message = (_("Invalid email address:\n- %s") %
                       first(bad_records).email)
            raise exceptions.ValidationError(message)

    @api.model
    def _sanitize_vals(self, vals):
        email = vals.get("email")
        if email:
            email = self._sanitize_email(email)
            # on dev or test redirect all emails to a centralized test mailbox
            sanitize = self._context.get('with_sanitize', True)
            if email and RUNNING_ENV != 'prod' and '@' in email and sanitize:
                if MASK and not RE_MASK.match(email):
                    email = email.replace('+', '-').replace('@', '-at-')
                    email = MASK % email
            vals["email"] = email

    @api.model
    def _sanitize_email(self, email):
        return email.replace(' ', '').lower() or False

    @api.model
    def create(self, vals):
        self._sanitize_vals(vals)
        return super().create(vals)

    @api.multi
    def write(self, vals):
        self._sanitize_vals(vals)
        return super().write(vals)

    @api.multi
    @api.onchange("email")
    def onchange_email(self):
        for coordinate in self:
            if coordinate.email:
                coordinate.email = self._sanitize_email(coordinate.email)
