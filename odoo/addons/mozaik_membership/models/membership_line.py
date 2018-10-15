# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date
from odoo import api, exceptions, models, fields, _
from odoo.tools import float_is_zero
import odoo.addons.decimal_precision as dp


class MembershipLine(models.Model):

    _name = 'membership.line'
    _inherit = ['mozaik.abstract.model']
    _description = 'Membership Line'
    _rec_name = 'partner_id'
    _order = 'date_from desc, date_to desc, create_date desc, partner_id'
    # 1 active membership line per partner/instance
    _unicity_keys = 'partner_id, int_instance_id'

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Member',
        ondelete='cascade', required=True, index=True)
    product_id = fields.Many2one(
        comodel_name='product.product', string='Subscription',
        domain="[('membership', '!=', False)]",
        index=True)
    state_id = fields.Many2one(
        comodel_name='membership.state', string='State',
        required=True, index=True)
    state_code = fields.Char(
        related='state_id.code', readonly=True, store=True)
    int_instance_id = fields.Many2one(
        comodel_name='int.instance', string='Internal Instance', index=True,
        default=lambda s: s._default_int_instance_id(), required=True,)
    reference = fields.Char(
        copy=False,
    )
    date_from = fields.Date(string='From', readonly=True)
    date_to = fields.Date(string='To', readonly=True)
    price = fields.Float(
        digits=dp.get_precision('Product Price'),
        copy=False,
    )

    partner_instance_ids = fields.Many2many(
        comodel_name="int.instance",
        string='Partner Internal Instances',
        related='partner_id.int_instance_ids',
        readonly=True,
    )

    _sql_constraints = [
        ('unique_ref', 'unique(reference)', 'This reference is already used'),
    ]

    @api.multi
    @api.constrains('reference', 'price')
    def _constrains_reference(self):
        """
        Constrain function for the field reference
        This field must be mandatory when the price is != 0.0.
        :return:
        """
        bad_records = self.filtered(
            lambda r: not r.price_is_zero(r.price) and not r.reference)
        if bad_records:
            details = "\n- ".join(bad_records.mapped("display_name"))
            message = _("A reference is mandatory when the price is greater "
                        "than 0:\n- %s") % details
            raise exceptions.ValidationError(message)

    @api.multi
    @api.constrains('partner_id')
    def _constrains_partner_id(self):
        """
        Constrain function for the field partner_id
        :return:
        """
        bad_records = self.filtered(lambda r: r.partner_id.is_company)
        if bad_records:
            details = "\n- ".join(bad_records.mapped("display_name"))
            message = _("It's not possible to create membership line for "
                        "a legal person:\n- %s") % details
            raise exceptions.ValidationError(message)

    @api.model
    def _default_int_instance_id(self):
        return self.env['int.instance']._get_default_int_instance()

    @api.model
    def _where_calc(self, domain, active_test=True):
        '''
        Read always inactive membership lines
        '''
        return super()._where_calc(domain, active_test=False)

    @api.multi
    def action_invalidate(self, vals=None):
        """
        Invalidates membership lines
        :rparam: True
        :rtype: boolean
        """
        vals = vals or {}
        if 'date_to' not in vals:
            vals.update({
                'date_to': fields.date.today(),
            })
        return super().action_invalidate(vals=vals)

    @api.model
    def _get_exception_messages(self):
        """
        Build a dict where the key is the constraint name (index name) and the
        value is the error message to raise (with a ValidationError).
        :return: dict
        """
        result = super(MembershipLine, self)._get_exception_messages()
        index_name = self._get_index_name()
        message = _("The partner already have an active subscription "
                    "to this instance")
        result.update({
            index_name: message,
        })
        return result

    @api.model
    def _invalidate_previous_lines(self, partner_ids, date_to, line_id=False,
                                   int_instance_id=False):
        """
        Based on given partner_ids and date_from, invalidate membership
        lines related to these one (every lines where date_to not filled).
        If a line_id is set, we only have to display a single membership
        line. This use case is used when we have a specific line to disable.
        For this case, we should have only 1 partner into partner_ids list.
        Example:
        - If a partner have 2 membership lines active (date_to is False and
            related to same instance), we have to disable these 2 lines.
        :param partner_ids: list of int
        :param date_to: str
        :param line_id: int
        :param int_instance_id: int
        :return: bool
        """
        if not partner_ids or not date_to:
            return False
        partners = self.env['res.partner'].browse(partner_ids)
        if not line_id:
            lines = partners.mapped("membership_line_ids").filtered(
                lambda l: not l.date_to)
            if int_instance_id:
                lines = lines.filtered(
                    lambda l: l.int_instance_id.id == int_instance_id)
        else:
            lines = self.browse(line_id)
        if lines:
            return lines.action_invalidate({
                'date_to': date_to,
            })
        return True

    @api.model
    def create(self, vals):
        """
        During the creation of a new membership.line, we have first to
        invalidate (by filling the date_to) of the previous membership line of
        the related partner.
        :param vals: dict
        :return: self recordset
        """
        if self.env.context.get(
                'no_invalidate_previous_membership_line', True):
            partner_id = vals.get('partner_id')
            date_from = vals.get('date_from')
            int_instance_id = vals.get('int_instance_id')
            self._invalidate_previous_lines(
                partner_ids=[partner_id], date_to=date_from,
                int_instance_id=int_instance_id)
        result = super(MembershipLine, self).create(vals)
        # With membership lines the force instance must be reset
        result.partner_id.force_int_instance_id = False
        return result

    @api.model
    def _get_subscription_product(self, partner, instance=False):
        """
        Get the subscription product related to the current partner
        The membership_line parameter could be used to have information about
        the instance, product etc
        :param partner: res.partner recordset
        :param instance: int.instance recordset
        :return: product.product recordset
        """
        partner.ensure_one()
        return partner.subscription_product_id

    @api.model
    def _get_subscription_price(self, product, partner=False, instance=False):
        """
        Get the subscription price based on given product.
        The price depends on the product, partner and the instance
        :param product: product.product recordset
        :param partner: res.partner recordset
        :param int.instance: int.instance recordset
        :return: float
        """
        product.ensure_one()
        return product.price or product.list_price

    @api.model
    def _generate_membership_reference(self, partner, instance, ref_date=''):
        """
        Generate a unique reference based on the partner, instance and the
        ref_date.
        This method is intended to be overriden regarding
        locale conventions.
        Here is an arbitrary convention: "MS: YYYY/id/id"
        :param partner: res.partner recordset
        :param instance: int.instance recordset
        :param ref_date: str/date
        :return:
        """
        partner.ensure_one()
        ref_date = ref_date or fields.Date.from_string(
            fields.Date.today()).year
        ref = 'MS: %s/%s/%s' % (ref_date, instance.id, partner.id)
        return ref

    @api.model
    def _build_membership_values(
            self, partner, instance, state,
            date_from=False, previous=False, product=False, price=None):
        """
        Build membership values based on given parameters
        :param partner: res.partner recordset
        :param instance: int.instance recordset
        :param state: membership.state recordset
        :param date_from: date/str
        :param previous: membership.line recordset
        :param product: product.product recordset
        :param price: float
        :return: dict
        """
        if not previous:
            previous = self.env[self._name].browse()
        if not product:
            product = self._get_subscription_product(
                partner=partner, instance=instance)
        date_from = date_from or fields.Date.today()
        # If the price is not given, we have to compute it
        if price is None:
            price = previous._get_subscription_price(
                product, partner=partner, instance=instance)
        reference = previous._generate_membership_reference(
            partner, instance, ref_date=date_from)
        values = {
            'date_from': date_from,
            'date_to': False,
            'partner_id': partner.id,
            'state_id': state.id,
            'int_instance_id': instance.id,
        }
        # TODO: add a awaiting_payment flag on membership.state model
        subscription_state_codes = [
            'member', 'member_candidate',
            'former_member_committee', 'member_committee',
        ]
        if state.code in subscription_state_codes:
            values.update({
                'price': price,
                'reference': reference,
                'product_id': product.id,
            })
        return values

    @api.model
    def price_is_zero(self, price):
        """
        Check if the given price is a zero (using the precision of the field)
        :param price: float
        :return: bool
        """
        precision = self._fields.get('price').digits[1]
        is_zero = float_is_zero(price, precision_digits=precision)
        return is_zero

    @api.model
    def _get_date_no_renew(self):
        """
        Get the date where we don't have to renew the membership.line
        :return: date
        """
        # Minus 1 because it's launched at the beginning of year
        year = date.today().year - 1
        # If we don't have a value, use the last day of year
        value = self.env['ir.config_parameter'].sudo().get_param(
            'membership.no_subscription_renew', default='31/12')
        day, month = [int(v) for v in value.split('/')]
        return date(year=year, month=month, day=day)

    @api.model
    def _get_forced_states_for_closing(self):
        """
        During the closing of membership.line, it's possible to force
        to close only lines with states defined returned by this function
        :return: membership.state recordset
        """
        return self.ref('mozaik_membership.member')

    @api.model
    def _get_lines_to_close(self):
        """
        Get membership lines to close (date_to is not filled)
        :return: membership.line recordset
        """
        domain = [
            ('date_to', '=', False),
            ('active', '=', True),
        ]
        states = self._get_forced_states_for_closing()
        if states:
            domain.append(('state_id', 'in', states.ids))
        context = self.env.context
        active_domain = context.get('active_domain')
        if context.get('active_model') == self._name and active_domain:
            domain.extend(active_domain)
        return self.search(domain)

    @api.multi
    def _close(self, date_to=False):
        """

        :param date_to: date/str
        :return: current recordset
        """
        if not date_to:
            date_to = fields.Date.today()
        if isinstance(date_to, str):
            real_date_to = fields.Date.from_string(date_to)
        # We can not renew if the date_from is < date_to
        lines = self.filtered(
            lambda l: fields.Date.from_string(l.date_from) <= real_date_to)
        if lines:
            values = {
                'date_to': date_to,
            }
            lines.action_invalidate(values)
        return lines

    @api.model
    def _get_lines_to_renew(self):
        """
        Get membership lines to renew.
        Load every lines where the date_from <= the limit_date
        (cfr: _get_date_no_renew() function)
        Then filter these lines to have only 1 line to renew per
        partner/instance.
        :return: membership.line recordset
        """
        limit_date = self._get_date_no_renew()
        domain = [
            # Active should be False to avoid constraint error during renew
            ('active', '=', False),
            ('date_from', '<=', limit_date),
        ]
        context = self.env.context
        active_domain = context.get('active_domain')
        if context.get('active_model') == self._name and active_domain:
            # We don't care about active/inactive because the renew have 2
            # behaviours (1 for active and another for inactive)
            domain = active_domain
        lines = self.search(domain, order='date_to ASC, id ASC')
        # Now we have every lines but we have to remove duplicates
        # (we should have 1 line per partner/instance)
        # So now we have for each combination partner/instance
        # only 1 membership line.
        # And thanks to the order (during search), the membership line should
        # be the last (more recent) membership line (so the one to renew)
        data = {(l.partner_id, l.int_instance_id): l for l in lines}
        # Now we have to get only membership lines (so dict values)
        membership_lines = self.browse()
        # .values() return a list but we need a multi-recordset
        for line in data.values():
            membership_lines |= line
        return membership_lines

    @api.multi
    def _renew(self, date_from=False):
        """
        Renew current membership.line
        :param date_from: str/date
        :return: membership.line recordset
        """
        membership_line_obj = self.env[self._name]
        limit_date = self._get_date_no_renew()
        # We have to renew every (active) membership lines of the partner
        if date_from:
            real_date_from = fields.Date.from_string(date_from)
        else:
            real_date_from = fields.Date.today()
        membership_lines = self.filtered(
            lambda l:
            fields.Date.from_string(l.date_from) <= limit_date and
            fields.Date.from_string(l.date_from) <= real_date_from)
        renewal_state = self.env.ref('mozaik_membership.member')
        # Save which membership line are created/updated
        membership_altered = membership_line_obj.browse()
        for membership_line in membership_lines:
            partner = membership_line.partner_id
            instance = membership_line.int_instance_id
            values = self._build_membership_values(
                partner, instance, renewal_state, date_from=real_date_from,
                previous=membership_line)
            # If the line still active, we only have to renew the reference
            # Because membership lines are supposed to be closed.
            # If there are not, it's because we have to renew them, without
            # creating new lines
            if membership_line.active:
                membership_line.write({
                    'reference': values.get('reference'),
                })
                membership_altered |= membership_line
            else:
                membership_altered |= membership_line_obj.create(values)
        return membership_altered

    @api.model
    def _launch_renew(self, date_from=False):
        """
        Steps:
        - Get every lines to close
        - Close them
        - Get every lines to renew
        - Renew them
        :param date_from: str/date
        :return: membership.line recordset
        """
        self._get_lines_to_close()._close(date_to=date_from)
        return self._get_lines_to_renew()._renew(date_from=date_from)
