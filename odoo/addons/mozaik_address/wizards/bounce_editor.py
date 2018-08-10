# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields

FAILURE_AVAILABLE_TYPES = [
    ('nomail', 'No longer receives mail at the mentioned address'),
    ('moved', 'Moved'),
    ('bad', 'Incomplete/Invalid address'),
    ('unknown', 'Unknown'),
    ('refused', 'Refused'),
    ('deceased', 'Deceased'),
    ('unclaimed', 'Unclaimed'),
    ('improper', 'Improper box number'),
]


class bounce_editor(orm.TransientModel):

    _inherit = 'bounce.editor'

    _columns = {
        'reason': fields.selection(FAILURE_AVAILABLE_TYPES, 'Reason'),
    }

    _defaults = {
        'reason': False,
    }

    def onchange_reason(self, cr, uid, ids, reason, context=None):
        if not reason:
            return {}
        context = context or self.pool['res.users'].context_get(cr, uid)
        src = [x[1] for x in FAILURE_AVAILABLE_TYPES if x[0] == reason][0]
        value = False
        if context.get('lang'):
            name = '%s,reason' % self._inherit
            value = self.pool['ir.translation']._get_source(
                cr, uid, name, 'selection', context['lang'], src)
        if not value:
            value = src
        res = {'description': value}
        return {
            'value': res,
        }
