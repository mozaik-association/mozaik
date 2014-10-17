# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
