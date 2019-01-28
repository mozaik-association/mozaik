# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError


class Legislature(models.Model):

    _inherit = 'legislature'

    @api.model
    def write(self, vals):
        new_deadline_date = vals.get('deadline_date', False)
        if new_deadline_date:
            for legis in self:
                if legis.deadline_date != new_deadline_date:
                    if (datetime.strptime(new_deadline_date,
                                          DEFAULT_SERVER_DATE_FORMAT) <
                        datetime.strptime(fields.datetime.now(),
                                          DEFAULT_SERVER_DATETIME_FORMAT)):
                        raise ValidationError(
                            _('New deadline date must be greater or'
                              ' equal than today !'))
                    mandate_obj = self.pool.get('sta.mandate')
                    mandate = mandate_obj.search(
                        [('legislature_id', '=', legis.id),
                         ('deadline_date', '>', new_deadline_date)])
                    if mandate:
                        mandate.write({'deadline_date': new_deadline_date})
        return super().write(vals)
