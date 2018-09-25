# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import date

from odoo import api, models, fields, _
from odoo.fields import first
from odoo.exceptions import ValidationError

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)
# Constants
AVAILABLE_PARTNER_KINDS = [
    ('a', 'Assembly'),
    ('t', 'Technical'),
    ('c', 'Company'),
    ('p', 'Partner'),
    ('m', 'Member'),
]


class ResPartner(models.Model):

    _inherit = 'res.partner'

    int_instance_id = fields.Many2one(
        comodel_name='int.instance', string='Internal Instance', index=True,
        track_visibility='onchange',
        default=lambda s: s._default_int_instance_id())
    int_instance_m2m_ids = fields.Many2many(
        comodel_name='int.instance', string='Internal Instances')

    membership_line_ids = fields.One2many(
        comodel_name='membership.line', inverse_name='partner_id',
        string='Memberships')
    free_member = fields.Boolean()
    membership_state_id = fields.Many2one(
        comodel_name='membership.state', string='Membership State', index=True,
        track_visibility='onchange', copy=False,
        default=lambda s: s._default_membership_state_id())
    membership_state_code = fields.Char(
        related='membership_state_id.code', readonly=True)
    subscription_product_id = fields.Many2one(
        compute="_compute_subscription_product_id",
        comodel_name="product.product", string='Subscription', store=True)
    kind = fields.Selection(
        compute="_compute_kind", string='Partner Kind', compute_sudo=True,
        selection=AVAILABLE_PARTNER_KINDS, store=True)
    accepted_date = fields.Date()
    decline_payment_date = fields.Date()
    rejected_date = fields.Date()
    resignation_date = fields.Date()
    exclusion_date = fields.Date()
    reference = fields.Char()
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

    @api.model
    def _default_int_instance_id(self):
        return self.env['int.instance']._get_default_int_instance()

    def _default_membership_state_id(self):
        return self.env['membership.state']._get_default_state().id

    @api.multi
    @api.depends('membership_line_ids', 'membership_line_ids.active')
    def _compute_current_membership_line_id(self):
        for partner in self:
            current_membership_line_id = first(
                partner.membership_line_ids.filtered(lambda s: s.active))
            partner.current_membership_line_id = current_membership_line_id

    @api.multi
    @api.depends('is_assembly', 'is_company',
                 'identifier', 'membership_state_code')
    def _compute_kind(self):
        '''
        Compute the kind of partner, computed field used in ir.rule
        '''
        for partner in self:
            if partner.is_assembly:
                k = 'a'
            elif not partner.identifier:
                k = 't'
            elif partner.is_company:
                k = 'c'
            elif partner.membership_state_code == 'without_membership':
                k = 'p'
            else:
                k = 'm'
            partner.kind = k

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
        def_state_id = membership_state_obj._get_default_state()
        for partner in self.filtered(lambda s: not s.is_company):
            values['partner_id'] = partner.id
            values['state_id'] = partner.membership_state_id.id
            if values['state_id'] != def_state_id.id:
                values['int_instance_id'] = partner.int_instance_id.id \
                    if partner.int_instance_id else False
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

    @api.multi
    def _get_followers_assemblies(self):
        self.ensure_one()
        fol_ids = self.env["res.partner"]
        int_instance_id = self.env.context.get('new_instance_id')
        if not int_instance_id:
            int_instance = self.int_instance_id
        else:
            int_instance = self.env["int.instance"].browse(int_instance_id)
        if not int_instance:
            return fol_ids
        fol_ids = int_instance._get_instance_followers()
        return fol_ids

    @api.multi
    def _subscribe_assemblies(self, int_instance_id=None):
        # compute list of new followers
        fol_ids = []
        for partner in self:
            fol_ids = self.with_context(new_instance_id=int_instance_id)\
                ._get_followers_assemblies()
            if fol_ids:
                partner.message_subscribe(partner_ids=fol_ids.ids)
        return fol_ids

    @api.model
    def _change_instance(self, new_instance):
        """
        Update instance of partner
        """
        # update partner and send changing instance notification
        vals = {
            'int_instance_id': new_instance.id,
        }
        self.write(vals)

    @api.multi
    def _generate_membership_reference(self, ref_date=None):
        """
        This method is intended to be overriden regarding
        locale conventions.
        Here is an arbitrary convention: "MS: YYYY/id"
        """
        self.ensure_one()
        ref_date = ref_date or date.today().year
        ref = 'MS: %s/%s' % (ref_date, self.id)
        return ref

    @api.multi
    def _create_user(self, login, group_ids):
        """
        When creating a user from a partner,
        give a first value to its int_instance_m2m_ids collection
        """
        self.ensure_one()
        user = super()._create_user(login, group_ids)
        self.int_instance_m2m_ids = self.int_instance_id
        return user

    @api.multi
    @api.depends("membership_line_ids", "membership_line_ids.product_id")
    def _compute_subscription_product_id(self):
        for partner in self:
            membership_line = first(
                partner.membership_line_ids.filtered("active"))
            partner.subscription_product_id = membership_line.product_id

    @api.multi
    def _update_membership_reference(self):
        '''
        Update reference for each partner ids
        '''
        vals = {}
        for partner in self:
            vals['reference'] = partner._generate_membership_reference()
            partner.write(vals)

    @api.model
    def create(self, vals):
        '''
        If partner has an identifier then update its followers
        '''
        res = super().create(vals)
        if 'identifier' in vals:
            res._update_followers()
        return res

    @api.multi
    def write(self, vals):
        """
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
                      'cannot be transformed to a legal person'))

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

        res = super().write(vals)

        # add a membership lines if any
        for partner in p_add_line:
            data = previous_data.get(partner.id, {})
            partner._update_membership_line(
                ref=data.get('reference'),
                date_from=data.get('accepted_date'))

        # update partners followers
        if vals.get('int_instance_id'):
            p_upd_fol._update_followers()

        if 'int_instance_m2m_ids' in vals:
            rule_obj = self.env['ir.rule']
            rule_obj.clear_cache()

        return res

    @api.multi
    def _update_followers(self):
        '''
        Update followers list for each partner
        '''
        for partner_id in self:
            # reset former followers
            for coodinate in [partner_id.postal_coordinate_ids,
                              partner_id.phone_coordinate_ids,
                              partner_id.email_coordinate_ids]:
                if coodinate:
                    coodinate._update_followers()

    # State management
    @api.multi
    def register_free_membership(self):
        '''
        Accept free subscription as membership payment
        '''
        # Accept membership
        self.paid()
        # Get free subscription
        free_prd_id = self.env.ref('mozaik_membership.membership_product_free')
        vals = {
            'product_id': free_prd_id.id,
            'price': 0.0,
        }
        # Force free subscription
        for partner in self:
            partner.current_membership_line_id.write(vals)

    @api.multi
    def decline_payment(self):
        today = fields.date.today()
        vals = {'decline_payment_date': today}

        if self.membership_state_code == "member":
            self._update_state("former_member")
        else:
            self._update_state("supporter")

        return self.write(vals)

    @api.multi
    def _exclude_or_resign(self, field):
        vals = {field: fields.date.today()}
        self.write(vals)
        res = None
        if self.ids and len(self.ids) == 1:
            # go directly to the co-residency form if any
            coord = self.postal_coordinate_id
            if coord and coord.co_residency_id:
                res = coord.co_residency_id.get_formview_action()
        return res

    @api.multi
    def exclude(self):
        res = self._exclude_or_resign('exclusion_date')
        if self.membership_state_code == "member":
            self._update_state("expulsion_former_member")
        else:
            self._update_state("inappropriate_former_member")
        return res

    @api.multi
    def resign(self):
        res = self._exclude_or_resign('resignation_date')
        if self.membership_state_code == "member":
            self._update_state("resignation_former_member")
        elif self.membership_state_code == "former_member":
            self._update_state("break_former_member")
        else:
            self._update_state("former_supporter")
        return res

    def accept(self):
        self._update_state("member")

    def member_candidate(self):
        self._update_state("member_candidate")

    def supporter(self):
        self._update_state("supporter")

    def reset(self):
        if self.membership_state_code == "former_supporter":
            self._update_state("supporter")
        else:
            self._update_state("former_member")

    @api.multi
    def reject(self):
        today = fields.date.today()
        res = self.write({'rejected_date': today})
        self._update_state("refused_member_candidate")
        return res

    def paid(self):
        if self.membership_state_code == "former_member":
            self._update_state("former_member_committee")
        else:
            self._update_state("member_committee")

    @api.multi
    def _update_state(self, membership_state_code):
        """
        :type membership_state_code: char
        :param membership_state_code: code of `membership.state`
        """
        self.ensure_one()
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
