# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, tools


class IrRule(models.Model):

    _inherit = 'ir.rule'

    @api.model
    @tools.ormcache('self._uid', 'model_name', 'mode')
    def _compute_domain(self, model_name, mode="read"):
        '''
        Transform domain ('x', 'child_of', []) always evaluated to True (!)
        to the False domain
        '''
        dom = super()._compute_domain(model_name, mode=mode)
        if dom:
            dom = isinstance(dom, list) and dom or list(dom)
            for ind, d in enumerate(dom):
                if not isinstance(d, str) and len(d) == 3:
                    if d[1] == 'child_of' and not d[2]:
                        dom[ind] = (0, '=', 1)
        return dom

    @api.model
    def clear_cache(self):
        res = super().clear_cache()
        self._compute_domain.clear_cache(self)
        return res
