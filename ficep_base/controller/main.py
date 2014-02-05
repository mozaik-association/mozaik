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


class Controller():

    def __init__(self,cr, uid, context):
        self.cr = cr
        self.uid = uid
        self.context = context

    def replication(self,base_model, target_model, search_on_target, field_to_update):
        res_ids = base_model.pool.get(target_model).search(self.cr, self.uid, search_on_target)
        base_model.pool.get(target_model).write(self.cr,
                                                self.uid,
                                                res_ids,
                                                {field_to_update: False},
                                                context=self.context)

    def set_partner_id(self, base_model, new_id, model_field):
        base_model.browse(self.cr,
                          self.uid,
                          new_id,
                          context=None).partner_id.write({model_field: new_id})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
