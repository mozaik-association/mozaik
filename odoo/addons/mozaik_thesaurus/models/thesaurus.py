# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields, _
from openerp.addons.mozaik_base.base_tools import format_value


class Thesaurus(models.Model):

    _name = 'thesaurus'
    _inherit = ['mozaik.abstract.model']
    _description = 'Thesaurus'
    _order = 'name'

    _track = {
        'new_thesaurus_term_id': {
            'mozaik_thesaurus.mt_thesaurus_add_term':
                lambda self, cr, uid, obj, ctx=None: obj.new_thesaurus_term_id,
        },
    }

    name = fields.Char('Thesaurus', required=True, track_visibility='onchange')
    new_thesaurus_term_id = fields.Many2one(
        comodel_name='thesaurus.term', string='New Term to Validate',
        readonly=True, track_visibility='onchange')

    _unicity_keys = 'name'

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if not self.env.context('copy_allowed'):
            raise Warning(_('A Thesaurus cannot be duplicated!'))

    @api.multi
    def update_notification_term(self, newid=False):
        """
        Update the field new_thesaurus_term_id producing or not a notification
        """
        vals = {'new_thesaurus_term_id': newid}
        if not newid:
            # notrack=Tue: disable tracking notification when
            # resetting new term id
            self.with_context(mail_notrack=True).write(vals)
        else:
            self.write(vals)
