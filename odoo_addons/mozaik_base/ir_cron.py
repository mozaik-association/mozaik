# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_base, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_base is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_base is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_base.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp
import openerp.tools as tools

original_acquire_job = openerp.addons.base.ir.ir_cron.ir_cron._acquire_job


class ir_cron(openerp.addons.base.ir.ir_cron.ir_cron):

    @classmethod
    def _acquire_job(cls, db_name):
        '''
        Avoid annoying traces in console when debugging server
        at a low applicative level
        '''
        res = False
        go = True
        # go = False
        if tools.config.options.get('log_level', '') in ['debug_sql']:
            go = False
        elif tools.config.options.get('deactivate_cron', '0') == '1':
            go = False
        if go:
            res = original_acquire_job(db_name)
        return res

openerp.addons.base.ir.ir_cron.ir_cron._acquire_job = ir_cron._acquire_job
