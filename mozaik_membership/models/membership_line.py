# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import date, timedelta

from odoo import _, api, exceptions, fields, models
from odoo.osv import expression
from odoo.tools import float_is_zero

logger = logging.getLogger(__name__)


class MembershipLine(models.Model):

    _name = "membership.line"
    _inherit = ["mozaik.abstract.model"]
    _description = "Membership Line"
    _rec_name = "partner_id"
    _order = "date_from desc, date_to desc, create_date desc, partner_id"
    # 1 active membership line per partner/instance
    _unicity_keys = "partner_id, int_instance_id"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Member",
        ondelete="cascade",
        required=True,
        index=True,
        auto_join=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Subscription",
        domain="[('membership', '!=', False)]",
        index=True,
    )
    state_id = fields.Many2one(
        comodel_name="membership.state", string="State", required=True, index=True
    )
    state_code = fields.Char(related="state_id.code", readonly=True, store=True)
    int_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string="Internal Instance",
        index=True,
        default=lambda s: s._default_int_instance_id(),
        required=True,
    )
    reference = fields.Char(
        copy=False,
    )
    date_from = fields.Date(
        string="From", required=True, default=lambda s: fields.Date.today()
    )
    date_to = fields.Date(string="To", copy=False)
    price = fields.Float(
        digits="Product Price",
        copy=False,
    )

    partner_instance_ids = fields.Many2many(
        comodel_name="int.instance",
        string="Partner Internal Instances",
        related="partner_id.int_instance_ids",
        readonly=True,
    )

    can_update_product = fields.Boolean(
        compute="_compute_can_update_product",
    )

    _sql_constraints = [
        ("unique_ref", "unique(reference)", "This reference is already used"),
    ]

    @api.constrains("reference", "price")
    def _constrains_reference(self):
        """
        Constrain function for the field reference
        This field must be mandatory when the price is != 0.0.
        :return:
        """
        bad_records = self.filtered(
            lambda r: not r._price_is_zero(r.price) and not r.reference and r.active
        )
        if bad_records:
            details = "\n- ".join(bad_records.mapped("display_name"))
            message = (
                _("A reference is mandatory when the price is greater " "than 0:\n- %s")
                % details
            )
            raise exceptions.ValidationError(message)

    def _get_reference(self):
        # this method is for inheritance
        self.ensure_one()
        return self.reference

    @api.constrains("active", "date_to")
    def _constrains_active_date_to(self):
        """
        Constrain function for fields active and date_to
        Active is True if date_to is False and vice versa
        :return:
        """
        bad_records = self.filtered(lambda r: r.active == bool(r.date_to))
        if bad_records:
            details = "\n- ".join(bad_records.mapped("display_name"))
            message = (
                _("The active boolean is incompatible with " "the 'To' date:\n- %s")
                % details
            )
            raise exceptions.ValidationError(message)

    @api.constrains("partner_id")
    def _constrains_partner_id(self):
        """
        Constrain function for the field partner_id
        :return:
        """
        bad_records = self.filtered(lambda r: r.partner_id.is_company)
        if bad_records:
            details = "\n- ".join(bad_records.mapped("display_name"))
            message = (
                _(
                    "It's not possible to create membership line for "
                    "a legal person:\n- %s"
                )
                % details
            )
            raise exceptions.ValidationError(message)

    @api.constrains("partner_id")
    def _constrains_exclusion(self):
        """
        Constrain function to ensure that we have only 1 membership line
        for a excluded partner.
        :return:
        """
        # Get every membership lines where the partner is excluded and with
        # more than 1 active line
        bad_records = self.filtered(
            lambda r: r.partner_id.is_excluded
            and len(r.partner_id.membership_line_ids.filtered(lambda l: l.active)) > 1
        )
        if bad_records:
            details = "\n- ".join(bad_records.mapped("partner_id.display_name"))
            message = (
                _(
                    "These partners are excluded but you're trying to add "
                    "new membership lines without disabled exclusion "
                    "lines:\n- %s"
                )
                % details
            )
            raise exceptions.ValidationError(message)

    @api.model
    def _get_states_can_update_product(self):
        """
        Return the list of states for which the product can be updated
        on the membership line, if it is active.
        """
        return [
            "member",
            "member_candidate",
            "former_member_committee",
            "member_committee",
        ]

    @api.depends("active", "state_code")
    def _compute_can_update_product(self):
        """
        Domain to define when the button "Update product/price" must
        be visible in the membership.line tree view in res.partner form view.
        """
        allowed_states = self._get_states_can_update_product()
        for rec in self:
            rec.can_update_product = rec.active and rec.state_code in allowed_states

    @api.model
    def _default_int_instance_id(self):
        return self.env["int.instance"]._get_default_int_instance()

    @api.model
    def _where_calc(self, domain, active_test=True):
        """
        Read inactive membership lines if active_test
        is not specified in the context
        """
        active_test &= self._context.get("active_test", False)
        return super()._where_calc(domain, active_test=active_test)

    def action_invalidate(self, vals=None):
        """
        Invalidates membership lines
        :rparam: True
        :rtype: boolean
        """
        vals = vals or {}
        if "date_to" not in vals:
            vals.update(
                {
                    "date_to": fields.date.today(),
                }
            )
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
        message = _("The partner already have an active subscription to this instance")
        result.update(
            {
                index_name: message,
            }
        )
        return result

    @api.model
    def _invalidate_previous_lines(
        self, partner_ids, date_to, line_id=False, int_instance_id=False, unexclude=True
    ):
        """
        Based on given partner_ids and date_from, invalidate membership
        lines related to these one (every lines where date_to not filled).
        If a line_id is set, we only have to display a single membership
        line. This use case is used when we have a specific line to disable.
        For this case, we should have only 1 partner into partner_ids list.
        Example:
        - If a partner have 2 membership lines active (date_to is False and
            related to same instance), we have to disable these 2 lines.
        Also, if given partners are excluded (is_exclude = True),
        membership lines with exclusion states will be invalidated (only
        if un-exclude parameter is set to True)
        :param partner_ids: list of int
        :param date_to: str
        :param line_id: int
        :param int_instance_id: int
        :param unexclude: bool
        :return: bool
        """
        if not partner_ids or not date_to:
            return False
        partners = self.env["res.partner"].browse(partner_ids)
        if not line_id:
            lines = partners.mapped("membership_line_ids").filtered(
                lambda l: not l.date_to
            )
            if int_instance_id:
                lines = lines.filtered(
                    lambda l: l.int_instance_id.id == int_instance_id
                )
        else:
            lines = self.browse(line_id)
        # If a partner is excluded, we have to un-exclude him before
        # create new line
        if unexclude and any(partners.mapped("is_excluded")):
            state_obj = self.env["membership.state"]
            all_excl_states = state_obj._get_all_exclusion_states()
            lines |= partners.mapped("membership_line_ids").filtered(
                lambda l: l.active and l.state_id in all_excl_states
            )
        if lines:
            return lines.action_invalidate(
                {
                    "date_to": date_to,
                }
            )
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
        if not self.env.context.get("no_invalidate_previous_membership_line"):
            partner_id = vals.get("partner_id")
            date_from = vals.get("date_from")
            int_instance_id = vals.get("int_instance_id")
            self._invalidate_previous_lines(
                partner_ids=[partner_id],
                date_to=date_from,
                int_instance_id=int_instance_id,
            )
            partner = self.env["res.partner"].sudo().browse(partner_id)
            if int_instance_id and not partner.membership_line_ids.filtered(
                lambda s, i=int_instance_id: s.active and s.int_instance_id.id == i
            ):
                partner.force_int_instance_id = int_instance_id
        state = self.env["membership.state"].browse(vals["state_id"])
        if state.code == "member":
            partner = self.env["res.partner"].browse(vals["partner_id"])
            if partner.membership_state_id.code not in ["member", "without_membership"]:
                memberships = self.env["membership.line"].search(
                    [("active", "=", True), ("partner_id", "=", partner.id)]
                )
                memberships._close(force=True)
        # because of the related store, most users will failed since
        # they don't have the right to write on membership line model
        self.check_access_rights("create")
        result = super(MembershipLine, self.sudo()).create(vals)
        result = self.browse(result.ids)
        result.check_access_rule("create")
        if result.partner_id.force_int_instance_id:
            # With membership lines the force instance must be reset
            result.partner_id.force_int_instance_id = False
        return result

    def copy(self, default=None):
        """

        :param default: None or dict
        :return: self recordset
        """
        self.ensure_one()
        default = default or {}
        if not self.active:
            # If the line has been disabled, the copy start at the date_to
            default.update(
                {
                    "date_from": self.date_to,
                    "date_to": False,
                }
            )
        result = super(MembershipLine, self).copy(default=default)
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
    def _generate_membership_reference(self, partner, instance, ref_date=""):
        """
        Generate a unique reference based on the partner, instance and the
        ref_date.
        This method is intended to be overriden regarding
        locale conventions.
        Here is an arbitrary convention: "MS: YYYY/id/id"
        Add also a random value, to avoid unique problem
        :param partner: res.partner recordset
        :param instance: int.instance recordset
        :param ref_date: str/date
        :return:
        """
        partner.ensure_one()
        ref_date = fields.Date.from_string(ref_date or fields.Date.today()).year
        ref = "MS: %s/%s/%s" % (
            ref_date,
            instance.id,
            partner.id,
        )
        return ref

    @api.model
    def _build_membership_values(
        self,
        partner,
        instance,
        state,
        date_from=False,
        product=False,
        price=None,
        reference=None,
    ):
        """
        Build membership values based on given parameters
        :param partner: res.partner recordset
        :param instance: int.instance recordset
        :param state: membership.state recordset
        :param date_from: date/str
        :param product: product.product recordset
        :param price: float
        :return: dict
        """
        if not product:
            product = self._get_subscription_product(partner=partner, instance=instance)
        date_from = date_from or fields.Date.today()
        # If the price is not given, we have to compute it
        if price is None:
            price = self._get_subscription_price(
                product, partner=partner, instance=instance
            )
        if price > 0 and reference is None:
            reference = self._generate_membership_reference(
                partner, instance, ref_date=date_from
            )
        values = {
            "date_from": date_from,
            "date_to": False,
            "partner_id": partner.id,
            "state_id": state.id,
            "int_instance_id": instance.id,
        }
        subscription_state_codes = state._get_all_subscription_codes()
        if state.code in subscription_state_codes:
            values.update(
                {
                    "price": price,
                    "reference": reference,
                    "product_id": product.id,
                }
            )
        return values

    @api.model
    def _price_is_zero(self, price):
        """
        Check if the given price is a zero (using the precision of the field)
        :param price: float
        :return: bool
        """
        precision = self._fields.get("price").get_digits(self.env)[1]
        is_zero = float_is_zero(price, precision_digits=precision)
        return is_zero

    @api.model
    def _get_date_no_renew(self, ref_date=None):
        """
        Get the date where we don't have to renew the membership.line
        :param ref_date: Date the date of reference (today by default)
        :return: date
        """
        if isinstance(ref_date, str):
            ref_date = fields.Date.from_string(ref_date)
        if not ref_date or ref_date < date.today():
            ref_date = date.today()
        # Minus 1 because it's launched at the beginning of year
        year = ref_date.year - 1
        default = "31/12"
        # If we don't have a value, use the last day of year
        value = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("membership.no_subscription_renew", default=default)
        )
        day, month = [int(v) for v in value.split("/")]
        # Check if the renew is done at the end of the year. If it's the case,
        # we don't have to use this current year (and not the previous one).
        current_year_date = date(year=year + 1, month=month, day=day)
        if ref_date >= current_year_date:
            return current_year_date
        return date(year=year, month=month, day=day)

    @api.model
    def _get_forced_states_for_closing(self):
        """
        During the closing of membership.line, it's possible to force
        to close only lines with states defined returned by this function
        :return: membership.state recordset
        """
        return self.env.ref("mozaik_membership.member")

    @api.model
    def _get_lines_to_close_renew_domain(self):
        return [
            ("date_to", "=", False),
            ("active", "=", True),
        ]

    @api.model
    def _get_lines_to_close_renew(self):
        """
        - Close membership.line
        - Renew membership.line if necessary
        :return: membership.line recordset
        """
        domain = self._get_lines_to_close_renew_domain()
        return self._get_lines_to_close(domain)

    @api.model
    def _get_lines_to_close_domain(self):
        return [
            ("date_to", "=", False),
            ("active", "=", True),
        ]

    @api.model
    def _get_lines_to_close_former_member(self):
        """

        :return: membership.line recordset
        """
        domain = self._get_lines_to_close_domain()
        return self._get_lines_to_close(domain)

    @api.model
    def _get_lines_to_close_member_candidate(self):
        """

        :return: membership.line recordset
        """
        domain = self._get_lines_to_close_domain()
        return self._get_lines_to_close(
            domain, states=self.env.ref("mozaik_membership.member_candidate")
        )

    @api.model
    def _get_lines_to_close(self, domain, partners=False, states=False):
        """
        Get membership lines to close (date_to is not filled)
        :param domain: list of tuple
        :param partners: res.partner recordset
        :return: membership.line recordset
        """
        if not states:
            states = self._get_forced_states_for_closing()
        if states:
            domain.append(("state_id", "in", states.ids))
        if partners:
            domain.append(("partner_id", "in", partners.ids))
        context = self.env.context
        active_domain = context.get("active_domain")
        if context.get("active_model") == self._name and active_domain:
            domain = expression.AND([domain, active_domain])
        return self.search(domain)

    def _close(self, date_to=False, force=False):
        """
        Close current recordset (only when the date_from is <= to the limit
        date (set into configuration)).
        If force parameter is set to True, close them whatever the date_from.
        :param date_to: date/str
        :param force: bool
        :return: current recordset
        """
        logger.info("Closing %s membership.lines", len(self))
        if not date_to:
            date_to = fields.Date.today()
        date_from = fields.Date.from_string(date_to)
        limit_date = self._get_date_no_renew(date_from)
        # We can not renew if the date_from is < limit_date
        if force:
            lines = self
        else:
            lines = self.filtered(
                lambda l: fields.Date.from_string(l.date_from) <= limit_date
            )
        if lines:
            values = {
                "date_to": date_to,
            }
            # Write last membership state on related partners.
            lines.mapped("partner_id")._update_previous_membership_state()
            lines.action_invalidate(values)
        lines.with_context(update_flags=False).flush()
        return lines

    @api.model
    def _get_lines_to_renew_domain(self, force_lines=None, ref_date=None):
        limit_date = self._get_date_no_renew(ref_date)
        res = [
            # Active should be False to avoid constraint error during renew
            ("active", "=", False),
            ("date_from", "<=", limit_date),
        ]
        if force_lines:
            res.append(("id", "in", force_lines.ids))
        return res

    @api.model
    def _get_lines_to_renew(self, force_lines=False, ref_date=None):
        """
        Get membership lines to renew.
        Load every lines where the date_from <= the limit_date
        (cfr: _get_date_no_renew() function)
        Then filter these lines to have only 1 line to renew per
        partner/instance.
        :return: membership.line recordset
        """
        membership = self._get_membership_line(
            self._get_lines_to_renew_domain(force_lines=force_lines, ref_date=ref_date)
        )
        return membership

    @api.model
    def _get_membership_line(self, domain):
        context = self.env.context
        active_domain = context.get("active_domain")
        if context.get("active_model") == self._name and active_domain:
            # We don't care about active/inactive because the renew have 2
            # behaviours (1 for active and another for inactive)
            domain = active_domain
        lines = self.search(domain, order="date_to ASC, id ASC")
        # Now we have every lines but we have to remove duplicates
        # (we should have 1 line per partner/instance)
        # So now we have for each combination partner/instance
        # only 1 membership line.
        # And thanks to the order (during search), the membership line should
        # be the last (more recent) membership line (so the one to renew)
        data = {(line.partner_id, line.int_instance_id): line for line in lines}
        # Now we have to get only membership lines (so dict values)
        membership_lines = self.browse()
        # .values() return a list but we need a multi-recordset
        for line in data.values():
            membership_lines |= line
        return membership_lines

    def _update_membership(self, state, date_from=False, force=False):
        """

        :param state: membership.state recordset
        :param date_from: str/date
        :return: membership.line recordset
        """
        membership_line_obj = self.env[self._name]
        real_date_from = date_from or fields.Date.today()
        limit_date = self._get_date_no_renew(real_date_from)
        # We have to renew every (active) membership lines of the partner
        membership_lines = self
        if not force:
            membership_lines = self.filtered(
                lambda l: fields.Date.from_string(l.date_from) <= limit_date
            )
        # Save which membership line are created/updated
        membership_altered = membership_line_obj.browse()
        membership_size = len(membership_lines)
        for i, membership_line in enumerate(membership_lines, start=1):
            logger.info(
                "Create %s membership, follow-up of %s (%s/%s)",
                state.code,
                membership_line,
                i,
                membership_size,
            )
            partner = membership_line.partner_id
            if (
                state.code != "member"
                and partner.membership_state_id.code != "without_membership"
            ):
                continue
            instance = membership_line.int_instance_id
            values = membership_line._update_membership_values(
                partner, instance, state, date_from=real_date_from
            )
            # If the line still active, we only have to renew the reference
            # Because membership lines are supposed to be closed.
            # If there are not, it's because we have to renew them, without
            # creating new lines
            if membership_line.active:
                membership_line.write(
                    {
                        "reference": values.get("reference"),
                    }
                )
                membership_altered |= membership_line
            else:
                membership_altered |= membership_line_obj.create(values)
        return membership_altered

    def _update_membership_values(self, partner, instance, state, date_from):
        self.ensure_one()
        return self._build_membership_values(
            partner, instance, state, date_from=date_from
        )

    def _renew(self, date_from=False):
        """
        Renew current membership.line
        :param date_from: str/date
        :return: membership.line recordset
        """
        state = self.env.ref("mozaik_membership.member")
        lines = self._get_lines_to_renew(force_lines=self, ref_date=date_from)
        logger.info("Renewing %s membership.lines", len(lines))
        renewed = lines._update_membership(state, date_from=date_from)
        to_former = self - lines
        logger.info("Former member %s membership.lines", len(to_former))
        former = self.env["membership.line"]
        if to_former:
            member = self.env.ref("mozaik_membership.member")
            former_member = self.env.ref("mozaik_membership.former_member")
            former = to_former._change_state(member, former_member, date_from=date_from)
        return renewed + former

    @api.model
    def _launch_renew(self, date_from=False):
        """
        Steps:
        - Get every lines to close
        - Close them
        - Renew them
        :param date_from: str/date
        """
        close_lines = self._get_lines_to_close_renew()

        last_i = 0
        step = int(
            self.env["ir.config_parameter"].get_param(
                "membership.renewal_slice_size", default="300"
            )
        )
        for i in range(step, len(close_lines), step):
            close_lines[last_i:i]._close_and_renew(date_from=date_from)
            last_i = i
        close_lines[last_i:]._close_and_renew(date_from=date_from)

    def _job_close_and_renew(self, date_from=False):
        date_to = fields.Date.from_string(date_from) - timedelta(days=1)
        lines = self._close(date_to=fields.Date.to_string(date_to))
        if lines:
            lines = lines._renew(date_from=date_from)
            # We have to flush to trigger re-compute before erasing
            # the value of the previous membership state.
            lines.flush()
            lines.mapped("partner_id").write({"previous_membership_state_id": False})
        return lines

    def _close_and_renew(self, date_from=False):
        self.with_delay(
            description="Renew %s memberships" % len(self),
            channel="root.membership_close_and_renew",
        )._job_close_and_renew(date_from=date_from)

    @api.model
    def _launch_former_member(self, date_from=False):
        """
        Steps:
        - Get every lines to close
        - Close them
        - Renew them
        :param date_from: str/date
        """
        close_lines = self._get_lines_to_close_former_member()

        step = int(
            self.env["ir.config_parameter"].get_param(
                "membership.renewal_slice_size", default="300"
            )
        )
        if close_lines:
            last_i = 0
            member = self.env.ref("mozaik_membership.member")
            former_member = self.env.ref("mozaik_membership.former_member")
            for i in range(step, len(close_lines), step):
                close_lines[last_i:i]._close_and_change_state(
                    member, former_member, date_from=date_from
                )
                last_i = i
            close_lines[last_i:]._close_and_change_state(
                member, former_member, date_from=date_from
            )

    def _close_and_change_state(self, from_state, to_state, date_from=False):
        self.with_delay(
            description="Former member %s memberships" % len(self),
            channel="root.membership_close_and_former_member",
        )._job_close_and_change_state(from_state, to_state, date_from=date_from)

    def _job_close_and_change_state(self, from_state, to_state, date_from):
        date_to = fields.Date.from_string(date_from) - timedelta(days=1)
        lines = self._close(date_to=fields.Date.to_string(date_to), force=True)
        for membership in self:
            membership.partner_id.stored_reference = membership.reference
        if lines:
            lines = lines._change_state(
                from_state, to_state, date_from=date_from, force=True
            )
        return lines

    def _change_state(self, from_state, to_state, date_from=False, force=False):
        """
        Former member current membership.line
        :param date_from: str/date
        :return: membership.line recordset
        """
        sql_query = """
        SELECT ml.id
        FROM membership_line AS ml
        INNER JOIN membership_line as active_ml
        ON active_ml.active IS TRUE and active_ml.partner_id = ml.partner_id
        WHERE ml.id in %(ids)s AND active_ml.state_id = %(member_state_id)s
        """
        sql_values = {"ids": tuple(self.ids), "member_state_id": from_state.id}
        self.env.cr.execute(sql_query, sql_values)
        lines_result = [r[0] for r in self.env.cr.fetchall()]
        lines_keep_closed = self.browse(lines_result)
        lines = self - lines_keep_closed
        lines = lines.filtered(lambda s, m=from_state: s.state_id == m)
        return lines._update_membership(to_state, date_from=date_from, force=force)

    @api.model
    def _get_fields_to_update(self, mode):
        """
        When a line is reactivated remove the date_to
        """
        result = super()._get_fields_to_update(mode)
        if mode == "activate":
            result.update(
                {
                    "date_to": False,
                }
            )
        return result
