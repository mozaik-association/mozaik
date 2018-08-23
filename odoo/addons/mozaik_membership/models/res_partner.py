# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    _inherit = 'res.partner'

    _subscription_store_trigger = {
        'membership.line': (lambda self, cr, uid, ids, context=None:
                            self.pool['membership.line'].get_linked_partners(
                                cr, uid, ids, context=context),
                            ['product_id'], 10),
    }

    _partner_kind_store_trigger = {
        'res.partner': (lambda self, cr, uid, ids, context=None: ids,
                        [
                            'is_assembly', 'is_company',
                            'identifier', 'membership_state_id'
                        ], 10),
    }
    _columns = {
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance', select=True,
            track_visibility='onchange'),
        'int_instance_m2m_ids': fields.many2many(
            'int.instance', 'res_partner_int_instance_rel', id1='partner_id',
            id2='int_instance_id', string='Internal Instances'),

        'membership_line_ids': fields.one2many(
            'membership.line', 'partner_id', string='Memberships'),
        'free_member': fields.boolean('Free Member'),
        'membership_state_id': fields.many2one(
            'membership.state', string='Membership State', select=True,
            track_visibility='onchange'),
        'membership_state_code': fields.related('membership_state_id', 'code',
                                                string='Membership State Code',
                                                type="char", readonly=True),
        'subscription_product_id': fields.function(
            _get_product_id, type='many2one', relation="product.product",
            string='Subscription', store=_subscription_store_trigger),
        'kind': fields.function(
            _get_partner_kind, string='Partner Kind', type='selection',
            selection=AVAILABLE_PARTNER_KINDS,
            store=_partner_kind_store_trigger),
        'accepted_date': fields.date('Accepted Date'),
        'decline_payment_date': fields.date('Decline Payment Date'),
        'rejected_date': fields.date('Rejected Date'),
        'resignation_date': fields.date('Resignation Date'),
        'exclusion_date': fields.date('Exclusion Date'),

        'reference': fields.char('Reference'),
    }

    _defaults = {
        'int_instance_id': lambda self, cr, uid, ids, context = None:
            self.pool.get('int.instance').get_default(cr, uid),
    }

    current_membership_line_id = fields.Many2one(
        comodel_name='membership.line', string='Current Membership',
        compute='_compute_current_membership_line_id')

    local_voluntary = fields.Boolean(track_visibility='onchange')
    regional_voluntary = fields.Boolean(track_visibility='onchange')
    national_voluntary = fields.Boolean(track_visibility='onchange')
    local_only = fields.Boolean(
        track_visibility='onchange',
        help='Partner wishing to be contacted only by the local')
    amount = fields.Float(
        digits=dp.get_precision('Product Price'), readonly=True)

    @api.multi
    @api.depends('membership_line_ids', 'membership_line_ids.active')
    def _compute_current_membership_line_id(self):
        for partner in self:
            current_membership_line_id = partner.membership_line_ids.filtered(
                lambda s: s.active) or False
            partner.current_membership_line_id = current_membership_line_id

    def _get_partner_kind(self, cr, uid, ids, name, arg, context=None):
        '''
        Compute the kind of partner, computed field used in ir.rule
        '''
        flds = [
            'is_assembly', 'is_company', 'identifier', 'membership_state_code',
        ]
        res = {}
        vals = self.read(cr, SUPERUSER_ID, ids, flds, context=context)
        for val in vals:
            if val['is_assembly']:
                k = 'a'
            elif not val['identifier']:
                k = 't'
            elif val['is_company']:
                k = 'c'
            elif val['membership_state_code'] == 'without_membership':
                k = 'p'
            else:
                k = 'm'
            res[val['id']] = k
        return res

    @api.multi
    def _update_state(self, membership_state_code):
        """
        Update state of partner. Called by workflow.

        :type membership_state_code: char
        :param membership_state_code: code of `membership.state`
        """
        self.ensure_one()
        if not self.env.context.get('lang'):
            self = self.with_context(lang=self.lang)
        membership_state_obj = self.env['membership.state']
        state = membership_state_obj.search(
            [('code', '=', membership_state_code)], limit=1)

        vals = {
            'membership_state_id': state.id,
            'accepted_date': False,
            'decline_payment_date': False,
            'rejected_date': False,
            'resignation_date': False,
            'exclusion_date': False,
            'customer': membership_state_code in [
                'member_candidate',
                'member_committee',
                'member',
                'former_member',
                'former_member_committee',
            ],
            'reference': False,
            'amount': False,
        }

        if membership_state_code == 'supporter':
            vals['free_member'] = True

        if membership_state_code == 'member_candidate':
            vals['del_doc_date'] = False

        # force voluntaries fields if any
        if membership_state_code in [
                'without_membership', 'supporter', 'former_supporter']:
            vals.update({
                'local_voluntary': False,
                'regional_voluntary': False,
                'national_voluntary': False,
            })
        elif any([
            membership_state_code == 'member_candidate' and
            self.membership_state_code in [
                'without_membership', 'supporter'],
            membership_state_code == 'member_committee' and
                self.membership_state_code == 'supporter']):
            vals.update({
                'local_voluntary': True,
                'regional_voluntary': True,
                'national_voluntary': True,
            })

        # force local only field if any
        if membership_state_code in [
                'supporter', 'former_supporter', 'member_candidate',
                'member_committee', 'member', 'former_member',
                'former_member_committee']:
            vals['local_only'] = False

        res = self.write(vals)

        return res

    @api.multi
    def _update_membership_line(self, ref=False, date_from=False):
        """
        Search for a `membership.membership_line` for each partner
        If no membership_line exist:
        * then create one
        * else invalidate it updating its `date_to` and duplicate it
          with the right state
        """
        date_from = date_from or fields.Date.today()
        values = {
            'date_from': date_from,
            'date_to': False,
        }
        membership_line_obj = self.env['membership.line']
        membership_state_obj = self.env['membership.state']
        def_state_id = membership_state_obj._state_default_get()
        for partner in self.filtered(lambda s: not s.is_company):
            values['partner_id'] = partner.id
            values['state_id'] = partner.membership_state_id.id
            if values['state_id'] != def_state_id:
                values['int_instance_id'] = partner.int_instance_id and \
                    partner.int_instance_id.id or False,
                values['reference'] = ref
                current_membership_line_id = membership_line_obj.search(
                    [('partner_id', '=', partner.id), ('active', '=', True)],
                    limit=1)

                if current_membership_line_id:
                    # update and copy it
                    current_membership_line_id.action_invalidate(
                        vals={'date_to': date_from})
                    current_membership_line_id.copy(default=values)
                else:
                    # create first membership_line
                    membership_line_obj.create(values)

    @api.model
    def _process_accept_members(self):
        """
        Advance the workflow with the signal `accept`
        for all partners found
        """
        nb_days = self.env['ir.config_parameter'].get_param(
            'nb_days', default=DEFAULT_NB_DAYS)

        try:
            nb_days = int(nb_days)
        except ValueError:
            nb_days = DEFAULT_NB_DAYS
            _logger.info('It seems the ir.config_parameter(nb_days) '
                         'is not a valid number. DEFAULT_NB_DAYS=%s days '
                         'is used instead.' % DEFAULT_NB_DAYS)

        # [MIG/ola] TODO: domain to rewrite (come from a removed model)
        member_ids = self.search([('nb_days', '>=', nb_days)])
        partner_ids = member_ids.mapped('partner_id')

        partner_ids.signal_workflow('accept')

        return True

    def _get_followers_assemblies(
            self, cr, uid, pid, context=None):
        context = context or {}
        ia_obj = self.pool['int.assembly']
        int_instance_id = context.get('new_instance_id')
        if not int_instance_id:
            int_instance_id = self.browse(
                cr, uid, pid, context=context).int_instance_id.id
        if not int_instance_id:
            return False
        fol_ids = ia_obj.get_followers_assemblies(
            cr, uid, int_instance_id, context=context)
        return fol_ids or False

    def _subscribe_assemblies(
            self, cr, uid, ids, int_instance_id=None, context=None):
        # compute list of new followers
        ctx = dict(
            context or {},
            new_instance_id=int_instance_id
        )
        fol_ids = []
        for pid in ids:
            fol_ids = self._get_followers_assemblies(
                cr, uid, pid, context=ctx)
            self.message_subscribe(
                cr, uid, [pid], fol_ids, context=context)
        return fol_ids

    def _update_followers(self, cr, uid, ids, context=None):
        '''
        Update followers list for each partner
        '''
        for partner_id in ids:
            # reset former followers
            self.reset_followers(cr, uid, [partner_id], context=context)
            # subscribe assemblies on partner
            f_partner_ids = self._subscribe_assemblies(
                cr, uid, [partner_id], context=context)

            # subscribe assemblies on coordinates
            domain = [('partner_id', '=', partner_id)]
            for prefix in ['email', 'postal', 'phone']:
                obj = self.pool['%s.coordinate' % prefix]
                res_ids = obj.search(
                    cr, uid, domain, context=context)
                if res_ids:
                    obj.reset_followers(
                        cr, uid, res_ids, except_fol_ids=[partner_id],
                        context=context)
                    obj._update_followers(
                        cr, uid, res_ids, fol_ids=f_partner_ids,
                        context=context)

        return True

    @api.cr_uid_id_context
    def _change_instance(self, cr, uid, pid, new_instance_id, context=None):
        """
        Update instance of partner
        """
        # update partner and send changing instance notification
        vals = {
            'int_instance_id': new_instance_id,
        }
        self.write(cr, uid, [pid], vals, context=context)

    def _generate_membership_reference(self, cr, uid, partner_id,
                                       ref_date=None, context=None):
        """
        This method is intended to be overriden regarding
        locale conventions.
        Here is an arbitrary convention: "MS: YYYY/id"
        """
        ref_date = ref_date or date.today().year
        ref = 'MS: %s/%s' % (ref_date, partner_id)
        return ref

    def _update_user_partner(self, cr, uid, partner, vals, context=None):
        """
        When creating a user from a partner,
        give a first value to its int_instance_m2m_ids collection
        """
        vals = vals or {}
        vals['int_instance_m2m_ids'] = [(6, 0, [partner.int_instance_id.id])]
        super(res_partner, self)._update_user_partner(
            cr, uid, partner, vals, context=context)

    def _get_product_id(self, cr, uid, ids, name, arg, context=None):
        res = {}
        ml_values = self.pool['membership.line'].search_read(
            cr, uid, [('partner_id', 'in', ids), ('active', '=', True)],
            ['partner_id', 'product_id'], context=context)
        for val in ml_values:
            res[val['partner_id'][0]] = val.get('product_id') and\
                val['product_id'][0] or False,
        return res

    def _update_membership_reference(self, cr, uid, ids, context=None):
        '''
        Update reference for each partner ids
        '''
        vals = {}
        for partner_id in ids:
            vals['reference'] = self._generate_membership_reference(
                cr, uid, partner_id, context=context)
            self.write(cr, uid, partner_id, vals, context=context)

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Do not copy m2m fields.
        """
        default = default or {}
        default.update({
            'int_instance_m2m_ids': [],
        })
        res = super(res_partner, self).copy_data(cr, uid, ids, default=default,
                                                 context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        '''
        If partner has an identifier then update its followers
        '''
        if not vals.get('is_company', False):
            # Force the state here to avoid a security alert
            # when creating the workflow and updating the first time
            # the state of the new partner
            state_obj = self.pool['membership.state']
            vals.update({
                'membership_state_id': state_obj._state_default_get(
                    cr, uid, context=context),
            })
        res = super(res_partner, self).create(cr, uid, vals, context=context)
        if vals.get('identifier', 0) > 0:
            # do not update followers when simulating partner workflow
            # i.e. identifier = -1 (see get_partner_preview method)
            self._update_followers(cr, SUPERUSER_ID, [res], context=context)
        return res

    @api.multi
    def create_workflow(self):
        '''
        Create workflow only for natural persons
        '''
        naturals = self.filtered(lambda s: not s.is_company)
        res = super(ResPartner, naturals).create_workflow()
        return res

    @api.multi
    def write(self, vals):
        """
        Create or Delete workflow if necessary (according to the new
        is_company value)
        Update followers when changing internal instance
        Add membership line when changing internal instance or state
        Invalidate some caches when changing set of instances related to
        the user
        """
        if 'is_company' in vals:
            is_company = vals['is_company']
            p2d = self.filtered(lambda s, c=is_company: not s.is_company and c)
            if p2d.mapped('membership_line_ids'):
                raise ValidationError(
                    _('A natural person with membership history '
                      'cannot be transformed to a legal person')
                )
            p2c = self.filtered(lambda s, c=is_company: s.is_company and not c)
            super(ResPartner, p2c).create_workflow()
            p2d.delete_workflow()

            if is_company:
                # reset state for a company
                vals['membership_state_id'] = None

        p_upd_fol = self.env['res.partner']
        p_add_line = self.env['res.partner']
        if vals.get('int_instance_id'):
            int_instance_id = vals['int_instance_id']
            p_upd_fol = self.filtered(
                lambda s, ii=int_instance_id: s.int_instance_id.id != ii)
            p_add_line |= p_upd_fol
            # subscribe related assemblies before updating partner
            # followers list will be entirely reinitialize later
            p_upd_fol._subscribe_assemblies(int_instance_id=int_instance_id)

        previous_data = {}
        if vals.get('membership_state_id'):
            p_add_line |= self
            previous_data = self.read(['accepted_date', 'reference'])
            previous_data = {data['id']: data for data in previous_data}

        res = super(ResPartner, self).write(vals)

        # add a membership lines if any
        for partner in p_add_line:
            data = previous_data.get(partner.id, {})
            partner._update_membership_line(
                ref=data.get('reference'),
                date_from=data.get('accepted_date'))

        # update partners followers
        p_upd_fol.sudo()._update_followers()

        if 'int_instance_m2m_ids' in vals:
            rule_obj = self.env['ir.rule']
            rule_obj.clear_cache()

        return res

    def register_free_membership(self, cr, uid, ids, context=None):
        '''
        Accept free subscription as membership payment
        '''
        # Accept membership
        self.pool['res.partner'].signal_workflow(
            cr, uid, ids, 'paid', context=context)
        # Get free subscription
        imd_obj = self.pool['ir.model.data']
        free_prd_id = imd_obj.xmlid_to_res_id(
            cr, uid, 'mozaik_membership.membership_product_free')
        vals = {
            'product_id': free_prd_id,
            'price': 0.0,
        }
        # Force free subscription
        for partner in self.browse(cr, uid, ids, context=context):
            partner.current_membership_line_id.write(vals)

    def decline_payment(self, cr, uid, ids, context=None):
        ctx = dict(context or {}, do_not_track_twice=True)
        today = fields.date.today()
        return self.write(cr, uid, ids, {'decline_payment_date': today},
                          context=ctx)

    def reject(self, cr, uid, ids, context=None):
        ctx = dict(context or {}, do_not_track_twice=True)
        today = fields.date.today()
        return self.write(cr, uid, ids, {'rejected_date': today},
                          context=ctx)

    @api.multi
    def _exclude_or_resign(self, field):
        this = self.with_context(do_not_track_twice=True)
        vals = {field: fields.date.today()}
        this.write(vals)
        res = None
        if self.ids and len(self.ids) == 1:
            # go directly to the co-residency form if any
            coord = self.postal_coordinate_id
            if coord and coord.co_residency_id:
                res = coord.co_residency_id.get_formview_action()
                res = res and res[0] or None
        return res

    def exclude(self, cr, uid, ids, context=None):
        return self._exclude_or_resign(
            cr, uid, ids, 'exclusion_date', context=context)

    def resign(self, cr, uid, ids, context=None):
        return self._exclude_or_resign(
            cr, uid, ids, 'resignation_date', context=context)
