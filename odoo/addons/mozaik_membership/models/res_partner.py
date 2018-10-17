# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, exceptions, models, fields, _
from odoo.fields import first
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

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
        comodel_name='int.instance',
        string='Internal Instances',
        relation="res_partner_int_instance_manager",
        column1="partner_id",
        column2="int_instance_id",
    )
    force_int_instance_id = fields.Many2one(
        comodel_name='int.instance',
        string="Force instance",
        default=lambda s: s._default_force_int_instance_id(),
    )
    membership_line_ids = fields.One2many(
        comodel_name='membership.line', inverse_name='partner_id',
        string='Memberships', readonly=True)
    membership_state_id = fields.Many2one(
        comodel_name='membership.state',
        string='Membership State',
        index=True,
        compute="_compute_int_instance_ids",
        store=True,
        track_visibility='onchange',
        compute_sudo=True,
    )
    membership_state_code = fields.Char(
        related='membership_state_id.code', readonly=True)
    subscription_product_id = fields.Many2one(
        compute="_compute_subscription_product_id",
        comodel_name="product.product", string='Subscription', store=False)
    kind = fields.Selection(
        compute="_compute_kind", string='Partner Kind', compute_sudo=True,
        selection=AVAILABLE_PARTNER_KINDS, store=True)
    local_voluntary = fields.Boolean(track_visibility='onchange')
    regional_voluntary = fields.Boolean(track_visibility='onchange')
    national_voluntary = fields.Boolean(track_visibility='onchange')
    local_only = fields.Boolean(
        track_visibility='onchange',
        help='Partner wishing to be contacted only by the local')

    int_instance_ids = fields.Many2many(
        comodel_name='int.instance',
        string='Instances',
        compute="_compute_int_instance_ids",
        relation="res_partner_int_instance",
        column1="partner_id",
        column2="int_instance_id",
        store=True,
        compute_sudo=True,
    )

    @api.model
    def _default_force_int_instance_id(self):
        return first(self.env.user.partner_id.int_instance_m2m_ids)

    @api.multi
    @api.constrains('membership_line_ids', 'is_company')
    def _constrains_membership_line_ids(self):
        """
        Constrain function for the field membership_line_ids
        :return:
        """
        bad_records = self.filtered(
            lambda r: r.is_company and r.membership_line_ids)
        if bad_records:
            details = "\n- ".join(bad_records.mapped("display_name"))
            message = _("A legal person shouldn't have membership "
                        "lines:\n- %s") % details
            raise exceptions.ValidationError(message)

    @api.multi
    @api.depends(
        'is_assembly',
        'membership_line_ids.int_instance_id', 'force_int_instance_id',
        'city_id', 'city_id.int_instance_id',
        'membership_line_ids', 'membership_line_ids.state_id',
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
        for record in self:
            memberships = record.membership_line_ids.filtered(
                lambda l: l.active)
            instances = memberships.mapped("int_instance_id")
            if not instances and record.force_int_instance_id:
                instances = record.force_int_instance_id
            if not instances and record.country_id.enforce_cities:
                instances = record.city_id.int_instance_id
            if not instances:
                instances = default_instance
            record.int_instance_ids = instances
            record.membership_state_id = record._get_current_state()

    @api.multi
    def _get_current_state(self):
        """
        Get the state of the current partner.
        :return: membership.state recordset
        """
        self.ensure_one()
        state_obj = self.env['membership.state']
        state = state_obj.browse()
        if not self.is_assembly:
            memberships = self.membership_line_ids.filtered("active")
            states = memberships.mapped("state_id")
            # Get the highest priority of state
            if states:
                state = first(states.sorted(key=lambda s: s.sequence))
            else:
                state = state_obj._get_default_state()
        return state

    @api.multi
    @api.constrains('force_int_instance_id', 'membership_line_ids')
    def _check_force_int_instance_id(self):
        """
        Check if partner has an instance if no membership
        """
        self_sudo = self.sudo()
        for partner in self_sudo.filtered(lambda s: not s.membership_line_ids):
            if not partner.force_int_instance_id:
                raise exceptions.ValidationError(_(
                    "A partner without membership "
                    "must be linked to an internal instance"))

    @api.multi
    @api.depends('is_assembly', 'is_company',
                 'identifier', 'membership_state_id')
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
            elif partner.membership_state_id.code == 'without_membership':
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

    @api.multi
    def _open_co_residency(self):
        '''
        When excluding or resigning a member open its co-residency,
        maybe some infos have to be accordingly changed
        '''
        res = None
        if self.ids and len(self.ids) == 1:
            # go directly to the co-residency form if any
            coord = self.postal_coordinate_id
            if coord and coord.co_residency_id:
                res = coord.co_residency_id.get_formview_action()
        return res

    @api.multi
    def _write(self, vals):
        '''
        Update additional flags together with the recomputing
        of membership_state_id by inheriting the _write() low level
        implementation
        '''
        if self and vals.get('membership_state_id'):
            new_state_code = self.env['membership.state'].browse(
                vals['membership_state_id']).code
            dic = vals.copy()
            res = True
            for partner in self:
                dic.update(partner._update_flags(new_state_code))
                res &= super(ResPartner, partner)._write(dic)
        else:
            res = super()._write(vals)
        return res

    @api.multi
    def _update_flags(self, new_state_code):
        """
        Update additional flags when changing state
        :type membership_state_code: char
        :param membership_state_code: code of the new state
        """
        self.ensure_one()

        vals = {}

        # force voluntaries fields if any
        if new_state_code in [
                'without_membership', 'supporter', 'former_supporter']:
            vals.update({
                'local_voluntary': False,
                'regional_voluntary': False,
                'national_voluntary': False,
            })
        elif any([
                new_state_code == 'member_candidate' and
                self.membership_state_code in [
                    'without_membership', 'supporter'],
                new_state_code == 'member_committee' and
                self.membership_state_code == 'supporter']):
            vals.update({
                'local_voluntary': True,
                'regional_voluntary': True,
                'national_voluntary': True,
            })

        # force local only field if any
        if new_state_code in [
                'supporter', 'former_supporter', 'member_candidate',
                'member_committee', 'member', 'former_member',
                'former_member_committee'] and self.local_only:
            vals['local_only'] = False

        return vals

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
