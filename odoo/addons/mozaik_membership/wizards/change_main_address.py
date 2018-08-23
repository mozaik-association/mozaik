# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields


class change_main_address(orm.TransientModel):

    _inherit = 'change.main.address'

    _columns = {
        'keeping_mode': fields.integer(string='Mode'),
        # 1: mandatory
        # 2: user's choice
        # 3: forbiden
        'keep_instance': fields.boolean(
            string='Keep Previous Internal Instance?'),
        'old_int_instance_id': fields.many2one(
            'int.instance', string='Previous Internal Instance',
            ondelete='cascade'),
        'new_int_instance_id': fields.many2one(
            'int.instance', string='New Internal Instance',
            ondelete='cascade'),
    }

    def default_get(self, cr, uid, fields, context):
        """
        To get default values for the object.
        """
        context = dict(context or {})
        res = super(change_main_address, self).default_get(cr, uid, fields,
                                                           context=context)

        ids = context.get('active_ids') or context.get('active_id') and \
            [context.get('active_id')] or []

        res['keeping_mode'] = 1
        res['keep_instance'] = False

        if len(ids) == 1:
            if context.get('mode', 'new') == 'switch':
                # switch of a main coordinate to another existing coordinate
                model = context.get('active_model', False)
                self._switch_context(cr, uid, model, ids[0], context=context)
                ids = [context['active_id']]

            for partner in self.pool['res.partner'].browse(cr, uid, ids,
                                                           context=context):
                if partner.int_instance_id:
                    res['keep_instance'] = partner.is_company
                    res['old_int_instance_id'] = partner.int_instance_id.id
            res['keeping_mode'] = 3

        return res

    def onchange_address_id(self, cr, uid, ids, address_id,
                            old_int_instance_id, context=None):
        res = {}
        new_int_instance_id = False
        keeping_mode = 3
        if not old_int_instance_id:
            keeping_mode = 1
        elif address_id:
            adr = self.pool['address.address'].browse(cr, uid, address_id,
                                                      context=context)
            if adr.address_local_zip_id:
                new_int_instance_id = \
                    adr.address_local_zip_id.int_instance_id.id
            else:
                new_int_instance_id = self.pool['int.instance'].\
                    get_default(cr, uid, context=None)
            if old_int_instance_id != new_int_instance_id:
                keeping_mode = 2
        res.update({'new_int_instance_id': new_int_instance_id,
                    'keeping_mode': keeping_mode})
        return {'value': res}

    def button_change_main_coordinate(self, cr, uid, ids, context=None):
        """
        Change main coordinate for a list of partners
        * a new main coordinate is created for each partner
        * the previsous main coordinate is invalidates or not regarding
          the option ``invalidate_previous_coordinate``
        :raise: ERROR if no partner selected

        **Note**
        When launched from the partner form the partner id is taken ``res_id``
        """
        context = context or {}

        wizard = self.browse(cr, uid, ids, context=context)[0]
        if wizard.keeping_mode == 2 and wizard.keep_instance:
            context.update({'keep_current_instance': True})

        return super(change_main_address, self).button_change_main_coordinate(
            cr, uid, ids, context=context)
