# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
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

    int_instance_m2m_ids = fields.Many2many(
        comodel_name='int.instance', string='Internal Instances')
    force_int_instance_id = fields.Many2one(
        comodel_name='int.instance',
        string="Force instance",
        required=True,
        default=lambda s: s._default_force_int_instance_id(),
    )
    membership_line_ids = fields.One2many(
        comodel_name='membership.line', inverse_name='partner_id',
        string='Memberships', readonly=True)
    free_member = fields.Boolean()
    membership_state_id = fields.Many2one(
        comodel_name='membership.state', string='Membership State',
        index=True,
        compute="_compute_int_instance_ids",
        store=True,
        track_visibility='onchange',
    )
    membership_state_code = fields.Char(
        related='membership_state_id.code', readonly=True)
    subscription_product_id = fields.Many2one(
        compute="_compute_subscription_product_id",
        comodel_name="product.product", string='Subscription', store=False)
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

    int_instance_ids = fields.Many2many(
        comodel_name='int.instance',
        string='Instances',
        compute="_compute_int_instance_ids",
        store=True,
    )

    @api.model
    def _default_force_int_instance_id(self):
        return first(self.env.user.partner_id.int_instance_m2m_ids)

    @api.multi
    @api.depends(
        'is_assembly',
        'membership_line_ids.int_instance_id', 'force_int_instance_id',
        'city_id', 'city_id.int_instance_id',
    )
    def _compute_int_instance_ids(self):
        """
        Compute function the field int_instance_ids.
        Rule to fill the field:
        - Use instances on active membership lines
        - IF NO instances found: use the force_int_instance_id
        - IF NO instances found: use the instance set on the city_id
            (if the country force to have cities)
        - IF NO instances found: use the default instance
        :return:
        """
        default_instance = self.env['int.instance']._get_default_int_instance()
        default_state = self.env['membership.state']._get_default_state()
        for record in self:
            state = default_state if not record.is_assembly else False
            memberships = record.membership_line_ids.filtered(
                lambda l: l.active)
            instances = memberships.mapped("int_instance_id")
            states = memberships.mapped("state_id")
            if states:
                state = states.filtered(
                    lambda s: s.state_code == 'member') or first(state)
            if not instances and record.force_int_instance_id:
                instances = record.force_int_instance_id
            if not instances and record.country_id.enforce_cities:
                instances = record.city_id.int_instance_id
            if not instances:
                instances = default_instance
            record.int_instance_ids = instances
            record.membership_state_id = state

    @api.model
    def _default_int_instance_id(self):
        return self.env['int.instance']._get_default_int_instance()

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

    @api.model
    def _get_default_subscription_product(self):
        """

        :return: product.template
        """
        return self.env['product.product'].browse()

    @api.multi
    def _renew_membership_line(self, date_from=False):
        """
        Renew a subscription of current partners.
        So a new membership.line is created for each partners.
        Previous
        :param date_from: str/date
        :return:
        """
        partners = self.filtered(lambda s: not s.is_company)
        # We have to renew every (active) membership lines of the partner
        partners.mapped("membership_line_ids").filtered(
            lambda l: l.active)._renew(date_from=date_from)

    @api.multi
    def _create_user(self, login, group_ids):
        """
        When creating a user from a partner,
        give a first value to its int_instance_m2m_ids collection
        """
        self.ensure_one()
        user = super()._create_user(login, group_ids)
        self.int_instance_m2m_ids = self.int_instance_ids
        return user

    @api.multi
    @api.depends("membership_line_ids", "membership_line_ids.product_id")
    def _compute_subscription_product_id(self):
        tarification_obj = self.env['membership.tarification']
        for partner in self:
            product = tarification_obj._get_product_by_partner(partner)
            partner.subscription_product_id = product

    @api.multi
    def write(self, vals):
        """
        Update followers when changing internal instance
        Add membership line when changing internal instance or state
        Invalidate some caches when changing set of instances related to
        the user
        """
        if vals.get('is_company'):
            if self.filtered(
                    lambda s: not s.is_company and s.membership_line_ids):
                raise ValidationError(
                    _('A natural person with membership history '
                      'cannot be transformed to a legal person'))
        res = super().write(vals)
        if 'int_instance_m2m_ids' in vals:
            self.env['ir.rule'].clear_cache()
        return res

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
    def _generate_membership_reference(self, instance=False, ref_date=''):
        """
        Generate the reference value for the current partner
        :param instance: int.instance recordset
        :param ref_date: date/str
        :return:
        """
        self.ensure_one()
        membership_obj = self.env['membership.line']
        if isinstance(instance, bool):
            instance = self.env['int.instance'].browse()
        # If no instance provided and the current partner has only 1 active
        # membership.line, use the related instance.
        if not instance:
            instances = self.membership_line_ids.filtered(
                lambda l: l.active)
            if len(instances) == 1:
                instance = instances
        return membership_obj._generate_membership_reference(
            partner=self, instance=instance, ref_date=ref_date)

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

    @api.multi
    def action_add_membership(self):
        """

        :return: dict
        """
        self.ensure_one()
        action = self.env.ref(
            "mozaik_membership.add_membership_action").read()[0]
        context = self.env.context.copy()
        context.update({
            'active_id': self.id,
            'active_model': self._name,
        })
        action.update({
            'context': context,
        })
        return action
