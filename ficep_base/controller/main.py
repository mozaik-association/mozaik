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

    def __init__(self, cr, uid, context):
        self.cr = cr
        self.uid = uid
        self.context = context

    def check_unicity_main(self, base_model, target_model, target_domain, fields_to_update):
        """
        ==================
        Check Unicity Main
        ==================

        This method will check the unicity of the main coordinate by a generic way:
        * Firstly search existing records depending of the ``target_domain``
        * Next step update value for the ``fields_to_update`` for the ``base_model``
        :param base_model: A base model that can be
                           * phone.coordinate
                           * address.coordinate
                           * email.coordinate
        :type base_model: BaseModel
        :param target_model: the concerned  model of the action
        :type target_model: char
        :param fields_to_update: fields to update with their associated value
        :type fields_to_update: dictionary

        **Note **: ``base_model`` is unlike ``target_model`` because this way is more generic:
                    That lets the possibility to pool on other model from an other
        """
        res_ids = base_model.pool.get(target_model).search(self.cr, self.uid, target_domain)
        base_model.pool.get(target_model).write(self.cr,
                                                self.uid,
                                                res_ids,
                                                fields_to_update,
                                                context=self.context)

    def replicate(self, base_model, new_id, model_field):
        """
        =========
        replicate
        =========

        Symbolic write that will ``replicate`` the browse record having ``new_id``
        into the partner_id
        :param base_model: A base model that can be
                           * phone.coordinate
                           * address.coordinate
                           * email.coordinate
        :type base_model: BaseModel
        :param: new_id: is the id of the record to set into the field of the partner
        :type new_id: integer
        :param model_field: ``model_field`` contains the name of the field that will be
                            updated
        :type model_field: char
        """
        base_model.browse(self.cr,
                          self.uid,
                          new_id,
                          context=None).partner_id.write({model_field: new_id})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
