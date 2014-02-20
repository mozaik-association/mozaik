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

    def __init__(self, base_model, cr, uid, target_model=None):
        """
        ========
        __init__
        ========
        :param base_model: A base model that can be
                           * phone.coordinate
                           * address.coordinate
                           * email.coordinate
        :type base_model: BaseModel
        :param target_model: the concerned  model of the action
        :type target_model: char

        :post: initialize with all passing parameters
               self.target_model is base_mode._name if no target_model passing
               into the parameters
        """
        self.cr = cr
        self.uid = uid
        self.base_model = base_model
        if not target_model:
            self.target_model = base_model._name
        else:
            self.target_model = target_model
        self.obj = base_model.pool.get(self.target_model)

    def search_and_update(self, target_domain, fields_to_update, context=None):
        """
        ==================
        search_and_update
        ==================

        This method will check the unicity of the main coordinate by a generic way:
        * Firstly search existing records depending of the ``target_domain``
        * Next step update value for the ``fields_to_update`` for the ``base_model``
        :param fields_to_update: fields to update with their associated value
        :type fields_to_update: dictionary
        """
        res_ids = self.obj.search(self.cr, self.uid, target_domain)
        self.obj.write(self.cr,
                       self.uid,
                       res_ids,
                       fields_to_update,
                       context=context)

    def replicate(self, new_id, model_field, context=None):
        """
        =========
        replicate
        =========
        Symbolic write that will ``replicate`` the browse record having ``new_id``
        into the partner_id
        :param: new_id: is the id of the record to set into the field of the partner
        :type new_id: integer
        :param model_field: ``model_field`` contains the name of the field that will be
                            updated
        :type model_field: char
        """
        self.base_model.browse(self.cr,
                          self.uid,
                          new_id,
                          context=context).partner_id.write({model_field: new_id})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
